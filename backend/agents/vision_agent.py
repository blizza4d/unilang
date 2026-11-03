import logging
import time
from langchain_core.messages import SystemMessage
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from agents.prompts import VISION_PROMPT
from config import Settings
from utils.llm_factory import build_chat_model, build_image_message

logger = logging.getLogger("datanova.agents.vision")


class AgentError(Exception):
    def __init__(self, agent_name: str, message: str, error_code: str = "AGENT_ERROR"):
        super().__init__(f"[{agent_name}] {message}")
        self.agent_name = agent_name
        self.message = message
        self.error_code = error_code


def _is_transient_error(exc: BaseException) -> bool:
    if isinstance(exc, AgentError):
        return False
    msg = str(exc).lower()
    return any(err in msg for err in ["timeout", "429", "rate limit", "connection", "503", "500"])


def run_vision_agent(pages_b64: list[str], settings: Settings) -> str:
    """Invokes vision LLM to extract spatial hierarchy and transcription from page images."""
    if not pages_b64:
        raise AgentError("vision", "No pages provided for vision analysis.", "AGENT_VISION_FAILED")

    start_time = time.perf_counter()
    logger.info("Vision agent starting for %d pages.", len(pages_b64))

    model = build_chat_model(
        provider=settings.LLM_PROVIDER_VISION,
        model=settings.VISION_MODEL,
        settings=settings,
        temperature=0.0,
    )

    messages = [
        SystemMessage(content=VISION_PROMPT),
        build_image_message(
            "Transcribe and map the visual structure of this invoice according to the instructions.",
            pages_b64,
        ),
    ]

    @retry(
        retry=retry_if_exception_type(Exception),
        retry_error_callback=lambda state: (_ for _ in ()).throw(state.outcome.exception()),
        stop=stop_after_attempt(settings.LLM_MAX_RETRIES + 1),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    def _invoke() -> str:
        try:
            response = model.invoke(messages)
            content = str(response.content) if hasattr(response, "content") else str(response)
            return content
        except Exception as exc:
            if not _is_transient_error(exc):
                raise AgentError("vision", f"Non-transient vision failure: {str(exc)}", "AGENT_VISION_FAILED") from exc
            logger.warning("Transient vision error, retrying: %s", str(exc))
            raise

    try:
        raw_output = _invoke()
    except Exception as exc:
        raise AgentError("vision", f"Vision agent execution failed: {str(exc)}", "AGENT_VISION_FAILED") from exc

    cleaned = raw_output.strip()
    if cleaned.startswith("```markdown"):
        cleaned = cleaned[len("```markdown") :].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    duration = time.perf_counter() - start_time
    logger.info("Vision agent completed in %.2fs with %d characters output.", duration, len(cleaned))

    if len(cleaned) < 20:
        raise AgentError(
            "vision",
            "Vision agent returned insufficient or empty content.",
            "AGENT_VISION_FAILED",
        )

    return cleaned
