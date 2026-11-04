import json
import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from agents.prompts import CLASSIFIER_PROMPT
from config import get_settings

logger = logging.getLogger("datanova.agents.classifier")


class PageRange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doc_type: str = Field(description="Document type for this sub-range")
    start_page: int = Field(description="1-indexed start page")
    end_page: int = Field(description="1-indexed end page")


class DocumentClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doc_type: str = Field(default="invoice", description="Detected canonical document type")
    confidence: float = Field(default=0.9, description="Confidence score from 0.0 to 1.0")
    language: str = Field(default="en", description="Primary detected ISO 639-1 language code")
    script: str = Field(default="Latin", description="Writing system script (e.g. Latin, Devanagari, Arabic, CJK)")
    is_multi_document: bool = Field(default=False, description="True if PDF bundles multiple distinct documents")
    page_ranges: List[PageRange] = Field(default_factory=list, description="Sub-ranges if multi-document")
    reasoning: str = Field(default="", description="Causal reasoning for classification")


FAST_KEYWORD_RULES = [
    ("credit_note", [r"\bcredit\s*note\b", r"\bgutschrift\b", r"\bavoir\b", r"\bnota\s*de\s*cr[eé]dito\b", r"\bcredit\s*memo\b"]),
    ("purchase_order", [r"\bpurchase\s*order\b", r"\bbon\s*de\s*commande\b", r"\bbestellung\b", r"\borden\s*de\s*compra\b", r"\bp\.?o\.?\s*#?"]),
    ("bank_statement", [r"\bbank\s*statement\b", r"\bkontoauszug\b", r"\brelev[eé]\s*de\s*compte\b", r"\bestado\s*de\s*cuenta\b", r"\bopening\s*balance\b", r"\bclosing\s*balance\b"]),
    ("utility_bill", [r"\butility\s*bill\b", r"\belectricity\s*bill\b", r"\bkwh\b", r"\bmeter\s*reading\b", r"\bwater\s*board\b", r"\bbroadband\s*bill\b"]),
    ("delivery_note", [r"\bdelivery\s*note\b", r"\blieferschein\b", r"\bbon\s*de\s*livraison\b", r"\balbar[aá]n\b", r"\bpacking\s*slip\b", r"\bbill\s*of\s*lading\b"]),
    ("expense_report", [r"\bexpense\s*report\b", r"\bspesenabrechnung\b", r"\bnote\s*de\s*frais\b", r"\binforme\s*de\s*gastos\b", r"\breimbursable\s*expense\b"]),
    ("id_document", [r"\bpassport\b", r"\bdriver'?s?\s*license\b", r"\bnational\s*identity\b", r"\bresidence\s*permit\b", r"\brepublic\s*of\b", r"\bdate\s*of\s*birth\b"]),
    ("contract_summary", [r"\bmaster\s*services?\s*agreement\b", r"\bparties\s*hereto\b", r"\bgoverning\s*law\b", r"\bconfidentiality\s*agreement\b", r"\bterm\s*of\s*this\s*agreement\b"]),
    ("receipt", [r"\breceipt\b", r"\bquittung\b", r"\bre[cç]u\b", r"\brecibo\b", r"\bcashier\b", r"\bpos\s*terminal\b", r"\btip\s*amount\b"]),
    ("invoice", [r"\btax\s*invoice\b", r"\binvoice\b", r"\brechnung\b", r"\bfacture\b", r"\bfactura\b", r"\bfattura\b", r"\b[فf]اتورة\b", r"发票", r"請求書"]),
]


def fast_keyword_classify(text: str) -> Optional[DocumentClassification]:
    """Fast deterministic regex keyword classifier."""
    text_lower = text.lower()
    for doc_type, patterns in FAST_KEYWORD_RULES:
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return DocumentClassification(
                    doc_type=doc_type,
                    confidence=0.92,
                    language="en",
                    script="Latin",
                    is_multi_document=False,
                    page_ranges=[PageRange(doc_type=doc_type, start_page=1, end_page=1)],
                    reasoning=f"Matched deterministic canonical keyword pattern '{pattern}'",
                )
    return None


async def classify_document(spatial_markdown: str, override_type: Optional[str] = None) -> DocumentClassification:
    """Classify document using fast regex prefilter with LLM fallback."""
    if override_type and override_type != "auto":
        return DocumentClassification(
            doc_type=override_type,
            confidence=1.0,
            language="en",
            script="Latin",
            is_multi_document=False,
            page_ranges=[PageRange(doc_type=override_type, start_page=1, end_page=1)],
            reasoning=f"Manual user override: {override_type}",
        )

    # 1. Deterministic fast prefilter
    fast_match = fast_keyword_classify(spatial_markdown[:3000])
    if fast_match:
        return fast_match

    # 2. LLM classification fallback
    settings = get_settings()
    try:
        from agents.llm_factory import get_llm
        llm = get_llm("extractor")
        prompt = (
            f"{CLASSIFIER_PROMPT}\n\n"
            f"<document_text>\n{spatial_markdown[:4000]}\n</document_text>\n\n"
            f"Classify and return valid JSON conforming to DocumentClassification schema."
        )
        structured_llm = llm.with_structured_output(DocumentClassification)
        result: DocumentClassification = await structured_llm.ainvoke(prompt)
        if result.confidence < 0.60:
            result.doc_type = "unknown"
        return result
    except Exception as exc:
        logger.warning("LLM classification failed (%s); defaulting to unknown", exc)
        return DocumentClassification(
            doc_type="unknown",
            confidence=0.5,
            language="unknown",
            script="Unknown",
            is_multi_document=False,
            page_ranges=[],
            reasoning=f"Classification fallback: {exc}",
        )
