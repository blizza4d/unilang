from typing import List
from pydantic import BaseModel, ConfigDict, Field


class CreditNoteLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(default="", description="Description of credited item or adjustment")
    quantity: float = Field(default=1.0, description="Credited quantity")
    unit_price: float = Field(default=0.0, description="Unit rate")
    total_price: float = Field(default=0.0, description="Total credit for item")


class ExtractedCreditNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    credit_note_number: str = Field(default="", description="Credit note identifier")
    original_invoice_number: str = Field(default="", description="Referenced original invoice number")
    vendor_name: str = Field(default="", description="Vendor or issuer name")
    date: str = Field(default="", description="Issue date in YYYY-MM-DD")
    currency: str = Field(default="", description="ISO currency code")
    total_amount: float = Field(default=0.0, description="Credited total amount")
    tax_amount: float = Field(default=0.0, description="Credited tax or VAT amount")
    reason: str = Field(default="", description="Reason for credit: return, discount, overbilling")
    line_items: List[CreditNoteLineItem] = Field(default_factory=list, description="Credited items")
