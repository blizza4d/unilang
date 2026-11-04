import pytest
from pydantic import ValidationError
from agents.classifier_agent import fast_keyword_classify
from schemas.doc_types.receipt import ExtractedReceipt
from schemas.doc_types.purchase_order import ExtractedPurchaseOrder
from schemas.doc_types.credit_note import ExtractedCreditNote
from schemas.doc_types.bank_statement import ExtractedBankStatement
from schemas.doc_types.id_document import ExtractedIDDocument
from schemas.registry import get_schema_spec, list_supported_doc_types


def test_schema_registry_all_types():
    specs = list_supported_doc_types()
    assert len(specs) >= 10
    doc_types = {s["doc_type"] for s in specs}
    assert "invoice" in doc_types
    assert "receipt" in doc_types
    assert "purchase_order" in doc_types
    assert "credit_note" in doc_types
    assert "bank_statement" in doc_types
    assert "utility_bill" in doc_types
    assert "delivery_note" in doc_types
    assert "expense_report" in doc_types
    assert "id_document" in doc_types
    assert "contract_summary" in doc_types


def test_doc_type_sensitive_flag():
    id_spec = get_schema_spec("id_document")
    assert id_spec.sensitive is True
    bank_spec = get_schema_spec("bank_statement")
    assert bank_spec.sensitive is True
    inv_spec = get_schema_spec("invoice")
    assert inv_spec.sensitive is False


def test_pydantic_models_extra_forbid():
    valid_receipt = ExtractedReceipt(
        merchant="SuperStore",
        date="2026-05-10",
        total_amount=54.20,
    )
    assert valid_receipt.merchant == "SuperStore"

    # Forbid extra fields
    with pytest.raises(ValidationError):
        ExtractedReceipt.model_validate({"merchant": "Test", "unexpected_field": 123})


def test_fast_keyword_classifier():
    # Credit note
    c_res = fast_keyword_classify("Subject: Credit Note #CR-991 for refund")
    assert c_res is not None
    assert c_res.doc_type == "credit_note"

    # Purchase order
    po_res = fast_keyword_classify("Official PURCHASE ORDER P.O. #44590")
    assert po_res is not None
    assert po_res.doc_type == "purchase_order"

    # Bank statement
    b_res = fast_keyword_classify("Kontoauszug Bank Statement Opening Balance: $5,000")
    assert b_res is not None
    assert b_res.doc_type == "bank_statement"
