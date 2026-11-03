import difflib
from typing import Any, Dict, List, Tuple


def field_similarity(str1: Any, str2: Any) -> float:
    if str1 is None and str2 is None:
        return 1.0
    if str1 is None or str2 is None:
        return 0.0
    s1 = str(str1).strip().lower()
    s2 = str(str2).strip().lower()
    if s1 == s2:
        return 1.0
    return difflib.SequenceMatcher(None, s1, s2).ratio()


def number_match(val1: Any, val2: Any, tolerance: float = 0.02) -> bool:
    try:
        n1 = float(val1)
        n2 = float(val2)
        return abs(n1 - n2) <= max(tolerance, abs(n1) * 0.01)
    except (TypeError, ValueError):
        return False


def evaluate_extracted_fields(
    predicted: Dict[str, Any], ground_truth: Dict[str, Any]
) -> Dict[str, float]:
    scores = {}

    # String fields
    for field in ["invoice_number", "vendor_name", "date", "currency"]:
        sim = field_similarity(predicted.get(field), ground_truth.get(field))
        scores[field] = sim

    # Numeric fields
    for field in ["total_amount", "tax_amount"]:
        pred_val = predicted.get(field)
        gt_val = ground_truth.get(field)
        scores[field] = 1.0 if number_match(pred_val, gt_val) else 0.0

    # Line items F1 matching
    pred_items: List[Dict[str, Any]] = predicted.get("line_items") or []
    gt_items: List[Dict[str, Any]] = ground_truth.get("line_items") or []

    if not gt_items and not pred_items:
        line_item_f1 = 1.0
    elif not gt_items or not pred_items:
        line_item_f1 = 0.0
    else:
        matched = 0
        for g_item in gt_items:
            g_tot = g_item.get("total_price") if "total_price" in g_item else g_item.get("total")
            for p_item in pred_items:
                desc_sim = field_similarity(p_item.get("description"), g_item.get("description"))
                p_tot = p_item.get("total_price") if "total_price" in p_item else p_item.get("total")
                tot_sim = number_match(p_tot, g_tot)
                if desc_sim >= 0.70 and tot_sim:
                    matched += 1
                    break
        precision = matched / len(pred_items) if pred_items else 0.0
        recall = matched / len(gt_items) if gt_items else 0.0
        line_item_f1 = (
            (2 * precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

    scores["line_items_f1"] = line_item_f1
    return scores
