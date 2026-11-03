import logging
import time
from pydantic import BaseModel, ConfigDict
from langchain_core.messages import HumanMessage, SystemMessage

from agents.prompts import JUDGE_PROMPT
from agents.vision_agent import AgentError
from config import Settings
from schemas.document_schemas import (
    INVOICE_FIELD_NAMES,
    ExtractedInvoice,
    ValidationScore,
)
from utils.llm_factory import build_chat_model
from utils.math_validator import apply_math_overrides, run_math_report

logger = logging.getLogger("datanova.agents.judge")


class JudgeOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    scores: list[ValidationScore]


def run_judge_agent(
    spatial_markdown: str,
    invoice: ExtractedInvoice,
    settings: Settings,
) -> list[ValidationScore]:
    """Evaluates extraction accuracy and math consistency, applying deterministic overrides."""
    start_time = time.perf_counter()
    logger.info("Judge agent running verification.")

    math_report = run_math_report(invoice, settings.MATH_TOLERANCE)

    model = build_chat_model(
        provider=settings.LLM_PROVIDER_JUDGE,
        model=settings.JUDGE_MODEL,
        settings=settings,
        temperature=0.0,
    )

    try:
        structured_judge = model.with_structured_output(JudgeOutput, method="json_schema")
    except Exception:
        structured_judge = model.with_structured_output(JudgeOutput, method="function_calling")

    human_payload = (
        "## SPATIAL TEXT TRANSCRIPTION:\n"
        f"{spatial_markdown}\n\n"
        "## EXTRACTED INVOICE JSON:\n"
        f"{invoice.model_dump_json(indent=2)}\n\n"
        f"{math_report.to_prompt_text()}\n\n"
        "Return exactly 7 validation scores, one for each field in order: "
        f"{', '.join(INVOICE_FIELD_NAMES)}."
    )

    messages = [
        SystemMessage(content=JUDGE_PROMPT),
        HumanMessage(content=human_payload),
    ]

    try:
        raw_judge_result = structured_judge.invoke(messages)
        if isinstance(raw_judge_result, JudgeOutput):
            scores_raw = raw_judge_result.scores
        elif isinstance(raw_judge_result, dict) and "scores" in raw_judge_result:
            scores_raw = [ValidationScore.model_validate(s) for s in raw_judge_result["scores"]]
        else:
            raise ValueError(f"Unexpected judge output shape: {type(raw_judge_result)}")
    except Exception as exc:
        logger.warning("Judge LLM structured call failed (%s). Falling back to deterministic scores.", str(exc))
        scores_raw = []
        for fn in INVOICE_FIELD_NAMES:
            scores_raw.append(
                ValidationScore(
                    field_name=fn,
                    confidence_score=0.9 if math_report.all_passed else 0.5,
                    needs_review=not math_report.all_passed,
                    reasoning="Deterministic evaluation fallback.",
                )
            )

    scores_by_field: dict[str, ValidationScore] = {}
    for score in scores_raw:
        fn = score.field_name
        if fn in INVOICE_FIELD_NAMES:
            if fn not in scores_by_field:
                scores_by_field[fn] = score
            else:
                if score.confidence_score < scores_by_field[fn].confidence_score:
                    scores_by_field[fn] = score

    complete_scores: list[ValidationScore] = []
    for fn in INVOICE_FIELD_NAMES:
        if fn in scores_by_field:
            sc = scores_by_field[fn]
            needs_rev = sc.confidence_score < settings.REVIEW_THRESHOLD
            complete_scores.append(
                ValidationScore(
                    field_name=fn,
                    confidence_score=sc.confidence_score,
                    needs_review=needs_rev,
                    reasoning=sc.reasoning,
                )
            )
        else:
            complete_scores.append(
                ValidationScore(
                    field_name=fn,
                    confidence_score=0.0,
                    needs_review=True,
                    reasoning="Judge returned no score for this field.",
                )
            )

    final_scores = apply_math_overrides(complete_scores, math_report, settings.REVIEW_THRESHOLD)

    duration = time.perf_counter() - start_time
    logger.info("Judge agent completed in %.2fs. Failures: %s", duration, math_report.failing_fields)
    return final_scores
