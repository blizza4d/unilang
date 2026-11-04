from typing import List
from pydantic import BaseModel, ConfigDict, Field


class POLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: str = Field(default="", description="Product SKU or part number")
    description: str = Field(default="", description="Item description")
    quantity: float = Field(default=1.0, description="Quantity ordered")
    unit_price: float = Field(default=0.0, description="Unit price per item")
    total_price: float = Field(default=0.0, description="Total line item amount")


class ExtractedPurchaseOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")

    po_number: str = Field(default="", description="Purchase order identifier")
    buyer: str = Field(default="", description="Buyer or purchasing organization name")
    supplier: str = Field(default="", description="Supplier or vendor name")
    order_date: str = Field(default="", description="Order issue date in YYYY-MM-DD")
    delivery_date: str = Field(default="", description="Target delivery date in YYYY-MM-DD")
    currency: str = Field(default="", description="ISO currency code")
    total_amount: float = Field(default=0.0, description="Total purchase order value")
    line_items: List[POLineItem] = Field(default_factory=list, description="Ordered items")
