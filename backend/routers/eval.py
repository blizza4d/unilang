import json
import logging
from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status

from config import get_settings
from eval.run_eval import run_evaluation_suite

logger = logging.getLogger("datanova.routers.eval")
router = APIRouter(prefix="/api/v1/eval", tags=["Evaluation Harness"])


@router.get("/latest", response_model=Dict[str, Any])
async def get_latest_eval_report() -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_EVAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Evaluation harness is disabled by feature flag",
        )

    report_path = Path(__file__).resolve().parent.parent / "eval" / "eval_report.json"
    if not report_path.exists():
        logger.info("No prior eval report found. Generating benchmark report...")
        report = await run_evaluation_suite()
        return report

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read eval_report.json: {e}")
        return await run_evaluation_suite()


@router.post("/run", response_model=Dict[str, Any])
async def trigger_eval_run() -> Dict[str, Any]:
    settings = get_settings()
    if not settings.FEATURE_EVAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Evaluation harness is disabled",
        )
    return await run_evaluation_suite()
