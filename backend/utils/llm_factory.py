from functools import lru_cache
from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Settings


class ConfigurationError(Exception):
    """Raised when an LLM provider or API key is misconfigured."""
    pass


@lru_cache(maxsize=16)
def _build_cached_model(
    provider: str,
    model: str,
    temperature: float,
    timeout: int,
    max_retries: int,
    openai_key: str,
    google_key: str,
) -> BaseChatModel:
    if provider == "openai":
        if not openai_key:
            raise ConfigurationError("OPENAI_API_KEY must be provided for OpenAI models.")
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            api_key=openai_key,
        )
    elif provider == "google":
        if not google_key:
            raise ConfigurationError("GOOGLE_API_KEY must be provided for Google models.")
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            google_api_key=google_key,
        )
    else:
        raise ConfigurationError(f"Unsupported LLM provider: {provider}")


def build_chat_model(
    provider: str,
    model: str,
    settings: Settings,
    temperature: float = 0.0,
) -> BaseChatModel:
    return _build_cached_model(
        provider=provider,
        model=model,
        temperature=temperature,
        timeout=settings.LLM_TIMEOUT_SECONDS,
        max_retries=settings.LLM_MAX_RETRIES,
        openai_key=settings.OPENAI_API_KEY,
        google_key=settings.GOOGLE_API_KEY,
    )


def build_image_message(prompt: str, pages_b64: list[str]) -> HumanMessage:
    """Build a multimodal message containing page images in standard LangChain format."""
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    for b64 in pages_b64:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )
    return HumanMessage(content=content)
