from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from schemas.document_schemas import ExtractedInvoice
from schemas.doc_types.receipt import ExtractedReceipt
from schemas.doc_types.purchase_order import ExtractedPurchaseOrder
from schemas.doc_types.credit_note import ExtractedCreditNote
from schemas.doc_types.bank_statement import ExtractedBankStatement
from schemas.doc_types.utility_bill import ExtractedUtilityBill
from schemas.doc_types.delivery_note import ExtractedDeliveryNote
from schemas.doc_types.expense_report import ExtractedExpenseReport
from schemas.doc_types.id_document import ExtractedIDDocument
from schemas.doc_types.contract_summary import ExtractedContractSummary


class UnknownDocument(BaseModel):
    raw_text: str = ""
    notes: str = "Unrecognized document structure. Please assign a manual type."


class DocumentSchemaSpec:
    """Pluggable specification defining extraction, scoring, compliance and UI layouts."""

    def __init__(
        self,
        doc_type: str,
        title: str,
        version: int,
        pydantic_model: Type[BaseModel],
        field_names: List[str],
        extractor_prompt_addendum: str,
        judge_rules: List[str],
        validators: List[str],
        ui_layout: Dict[str, Any],
        sensitive: bool = False,
    ):
        self.doc_type = doc_type
        self.title = title
        self.version = version
        self.pydantic_model = pydantic_model
        self.field_names = field_names
        self.extractor_prompt_addendum = extractor_prompt_addendum
        self.judge_rules = judge_rules
        self.validators = validators
        self.ui_layout = ui_layout
        self.sensitive = sensitive

    def to_metadata(self) -> Dict[str, Any]:
        return {
            "doc_type": self.doc_type,
            "title": self.title,
            "version": self.version,
            "field_names": self.field_names,
            "validators": self.validators,
            "ui_layout": self.ui_layout,
            "sensitive": self.sensitive,
        }


# Schema definitions
SCHEMA_SPECS: Dict[str, DocumentSchemaSpec] = {
    "invoice": DocumentSchemaSpec(
        doc_type="invoice",
        title="Commercial Invoice",
        version=1,
        pydantic_model=ExtractedInvoice,
        field_names=[
            "vendor_name", "invoice_number", "invoice_date", "due_date",
            "currency", "subtotal", "tax_amount", "total_amount", "line_items"
        ],
        extractor_prompt_addendum="Extract invoice metadata, header fields, and line items with strict math integrity.",
        judge_rules=["Cross-check total with subtotal and taxes.", "Verify line items sum matches subtotal."],
        validators=["math_validator", "tax_id_validator", "date_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Vendor & Header", "fields": ["vendor_name", "invoice_number", "invoice_date", "due_date"]},
                {"title": "Financial Summary", "fields": ["currency", "subtotal", "tax_amount", "total_amount"]},
                {"title": "Line Items", "table": "line_items", "columns": ["description", "quantity", "unit_price", "total_price"]},
            ]
        },
        sensitive=False,
    ),
    "receipt": DocumentSchemaSpec(
        doc_type="receipt",
        title="Retail / POS Receipt",
        version=1,
        pydantic_model=ExtractedReceipt,
        field_names=[
            "merchant", "date", "time", "payment_method", "currency",
            "subtotal", "tax_amount", "tip", "total_amount", "line_items"
        ],
        extractor_prompt_addendum="Extract retail receipt details including store name, transaction timestamp, tip, and items.",
        judge_rules=["Ensure tip + subtotal + tax equals total_amount."],
        validators=["math_validator", "date_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Merchant & Payment", "fields": ["merchant", "date", "time", "payment_method"]},
                {"title": "Amounts", "fields": ["currency", "subtotal", "tax_amount", "tip", "total_amount"]},
                {"title": "Purchased Items", "table": "line_items", "columns": ["description", "quantity", "unit_price", "total_price"]},
            ]
        },
        sensitive=False,
    ),
    "purchase_order": DocumentSchemaSpec(
        doc_type="purchase_order",
        title="Purchase Order",
        version=1,
        pydantic_model=ExtractedPurchaseOrder,
        field_names=["po_number", "buyer", "supplier", "order_date", "delivery_date", "currency", "total_amount", "line_items"],
        extractor_prompt_addendum="Extract PO number, supplier, buyer entities, agreed delivery schedule and SKU items.",
        judge_rules=["Verify SKU items sum matches total_amount."],
        validators=["math_validator", "date_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Order Metadata", "fields": ["po_number", "order_date", "delivery_date"]},
                {"title": "Counterparties", "fields": ["buyer", "supplier"]},
                {"title": "Total", "fields": ["currency", "total_amount"]},
                {"title": "Ordered Items", "table": "line_items", "columns": ["sku", "description", "quantity", "unit_price", "total_price"]},
            ]
        },
        sensitive=False,
    ),
    "credit_note": DocumentSchemaSpec(
        doc_type="credit_note",
        title="Credit Note / Memo",
        version=1,
        pydantic_model=ExtractedCreditNote,
        field_names=["credit_note_number", "original_invoice_number", "vendor_name", "date", "currency", "total_amount", "tax_amount", "reason", "line_items"],
        extractor_prompt_addendum="Extract credit memo identifier, referenced invoice, reason for refund/credit, and credit items.",
        judge_rules=["Verify credit items sum matches credited total."],
        validators=["math_validator", "date_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Credit Note Info", "fields": ["credit_note_number", "original_invoice_number", "vendor_name", "date"]},
                {"title": "Credit Values", "fields": ["currency", "tax_amount", "total_amount", "reason"]},
                {"title": "Credited Items", "table": "line_items", "columns": ["description", "quantity", "unit_price", "total_price"]},
            ]
        },
        sensitive=False,
    ),
    "bank_statement": DocumentSchemaSpec(
        doc_type="bank_statement",
        title="Bank Statement",
        version=1,
        pydantic_model=ExtractedBankStatement,
        field_names=["account_holder", "account_number_masked", "bank_name", "period_start", "period_end", "currency", "opening_balance", "closing_balance", "transactions"],
        extractor_prompt_addendum="Extract bank account overview, masked account number, opening/closing balance, and transaction entries.",
        judge_rules=["Verify running balance formula: opening_balance + sum(credits) - sum(debits) equals closing_balance."],
        validators=["bank_reconciliation_validator", "date_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Account Details", "fields": ["account_holder", "account_number_masked", "bank_name"]},
                {"title": "Statement Period & Balance", "fields": ["period_start", "period_end", "currency", "opening_balance", "closing_balance"]},
                {"title": "Transactions", "table": "transactions", "columns": ["date", "description", "debit", "credit", "balance"]},
            ]
        },
        sensitive=True,
    ),
    "utility_bill": DocumentSchemaSpec(
        doc_type="utility_bill",
        title="Utility Bill",
        version=1,
        pydantic_model=ExtractedUtilityBill,
        field_names=["provider", "account_number_masked", "service_address", "billing_period_start", "billing_period_end", "due_date", "currency", "total_due", "usage_items"],
        extractor_prompt_addendum="Extract utility provider, meter/account details, billing window, and metered tariffs.",
        judge_rules=["Verify usage charges aggregate to total_due."],
        validators=["math_validator", "date_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Provider & Service Location", "fields": ["provider", "account_number_masked", "service_address"]},
                {"title": "Billing Window", "fields": ["billing_period_start", "billing_period_end", "due_date", "currency", "total_due"]},
                {"title": "Consumption Breakdown", "table": "usage_items", "columns": ["service_type", "units_consumed", "rate_per_unit", "charge_amount"]},
            ]
        },
        sensitive=False,
    ),
    "delivery_note": DocumentSchemaSpec(
        doc_type="delivery_note",
        title="Delivery Note / Packing Slip",
        version=1,
        pydantic_model=ExtractedDeliveryNote,
        field_names=["delivery_number", "supplier", "recipient", "date", "items"],
        extractor_prompt_addendum="Extract dispatch slip number, consignor/consignee, delivery date, and delivered quantities.",
        judge_rules=["Check for discrepancies between ordered and delivered counts."],
        validators=["date_validator"],
        ui_layout={
            "sections": [
                {"title": "Delivery Header", "fields": ["delivery_number", "supplier", "recipient", "date"]},
                {"title": "Delivered Items", "table": "items", "columns": ["sku", "description", "quantity_ordered", "quantity_delivered"]},
            ]
        },
        sensitive=False,
    ),
    "expense_report": DocumentSchemaSpec(
        doc_type="expense_report",
        title="Employee Expense Report",
        version=1,
        pydantic_model=ExtractedExpenseReport,
        field_names=["employee", "period", "currency", "total_amount", "expenses"],
        extractor_prompt_addendum="Extract submitter identity, reporting cycle, and categorized expense items.",
        judge_rules=["Verify sum of itemized expense rows equals total_amount."],
        validators=["math_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Employee & Period", "fields": ["employee", "period", "currency", "total_amount"]},
                {"title": "Expense Items", "table": "expenses", "columns": ["date", "category", "merchant", "amount"]},
            ]
        },
        sensitive=False,
    ),
    "id_document": DocumentSchemaSpec(
        doc_type="id_document",
        title="Identity Document",
        version=1,
        pydantic_model=ExtractedIDDocument,
        field_names=["document_type", "issuing_country", "full_name", "date_of_birth", "document_number_masked", "expiry_date"],
        extractor_prompt_addendum="Extract government ID type, issuing jurisdiction, holder full legal name, masked ID number, and expiry.",
        judge_rules=["Ensure holder date of birth is plausible.", "Verify expiry date is greater than issue date."],
        validators=["date_validator"],
        ui_layout={
            "sections": [
                {"title": "ID Overview", "fields": ["document_type", "issuing_country", "full_name"]},
                {"title": "Holder Data", "fields": ["date_of_birth", "document_number_masked", "expiry_date"]},
            ]
        },
        sensitive=True,
    ),
    "contract_summary": DocumentSchemaSpec(
        doc_type="contract_summary",
        title="Commercial Contract Summary",
        version=1,
        pydantic_model=ExtractedContractSummary,
        field_names=["parties", "effective_date", "term_months", "renewal_terms", "total_value", "currency", "governing_law", "termination_notice_days"],
        extractor_prompt_addendum="Extract contracting corporate entities, effective term, governing jurisdiction, renewal policy, and commitment values.",
        judge_rules=["Check that notice period and term months are positive integers."],
        validators=["date_validator", "currency_validator"],
        ui_layout={
            "sections": [
                {"title": "Parties & Jurisdiction", "fields": ["parties", "governing_law"]},
                {"title": "Term & Renewal", "fields": ["effective_date", "term_months", "renewal_terms", "termination_notice_days"]},
                {"title": "Commitment Value", "fields": ["currency", "total_value"]},
            ]
        },
        sensitive=False,
    ),
    "unknown": DocumentSchemaSpec(
        doc_type="unknown",
        title="Unclassified Document",
        version=1,
        pydantic_model=UnknownDocument,
        field_names=["raw_text", "notes"],
        extractor_prompt_addendum="Capture raw structural notes.",
        judge_rules=[],
        validators=[],
        ui_layout={"sections": [{"title": "General Notes", "fields": ["notes"]}]},
        sensitive=False,
    ),
}


def get_schema_spec(doc_type: str) -> DocumentSchemaSpec:
    """Retrieve schema specification by document type identifier."""
    return SCHEMA_SPECS.get(doc_type.lower(), SCHEMA_SPECS["unknown"])


def list_supported_doc_types() -> List[Dict[str, Any]]:
    """List all supported document schemas with titles and UI layout specifications."""
    return [spec.to_metadata() for spec in SCHEMA_SPECS.values() if spec.doc_type != "unknown"]
