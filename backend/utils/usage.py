import json
import logging
from config import get_settings
from schemas.grounding import UsageSummary

logger = logging.getLogger("datanova.usage")
settings = get_settings()


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float | None:
    try:
        price_table = json.loads(settings.PRICE_TABLE_JSON)
        rates = price_table.get(model)
        if not rates:
            return None

        in_rate = float(rates.get("input", 0.0)) / 1_000_000.0
        out_rate = float(rates.get("output", 0.0)) / 1_000_000.0

        cost = (input_tokens * in_rate) + (output_tokens * out_rate)
        return round(cost, 5)
    except Exception as exc:
        logger.debug("Cost calculation error: %s", str(exc))
        return None


def build_usage_summary(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> UsageSummary:
    cost = calculate_cost(model, input_tokens, output_tokens)
    return UsageSummary(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=cost,
    )
