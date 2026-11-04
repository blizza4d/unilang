from typing import List
from pydantic import BaseModel, ConfigDict, Field


class ReceiptLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(default="", description="Item description or name")
    quantity: float = Field(default=1.0, description="Quantity purchased")
    unit_price: float = Field(default=0.0, description="Unit price per item")
    total_price: float = Field(default=0.0, description="Total item price")


class ExtractedReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    merchant: str = Field(default="", description="Merchant or store name")
    date: str = Field(default="", description="Transaction date in YYYY-MM-DD format")
    time: str = Field(default="", description="Transaction time in HH:MM format")
    payment_method: str = Field(default="", description="Payment method: Cash, Visa, Mastercard, UPI, Amex")
    currency: str = Field(default="", description="ISO currency code (e.g. USD, EUR, INR)")
    subtotal: float = Field(default=0.0, description="Subtotal before taxes and tips")
    tax_amount: float = Field(default=0.0, description="Tax or VAT amount")
    tip: float = Field(default=0.0, description="Tip or gratuity amount")
    total_amount: float = Field(default=0.0, description="Final total amount paid")
    line_items: List[ReceiptLineItem] = Field(default_factory=list, description="Purchased items")
