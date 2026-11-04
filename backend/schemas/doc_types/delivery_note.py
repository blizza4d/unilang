from typing import List
from pydantic import BaseModel, ConfigDict, Field


class DeliveryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: str = Field(default="", description="Item SKU or article number")
    description: str = Field(default="", description="Product or package description")
    quantity_ordered: float = Field(default=0.0, description="Quantity originally ordered")
    quantity_delivered: float = Field(default=0.0, description="Quantity actually delivered")


class ExtractedDeliveryNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delivery_number: str = Field(default="", description="Delivery note / packing slip number")
    supplier: str = Field(default="", description="Supplier or dispatch company")
    recipient: str = Field(default="", description="Consignee or recipient name")
    date: str = Field(default="", description="Delivery / dispatch date in YYYY-MM-DD")
    items: List[DeliveryItem] = Field(default_factory=list, description="Delivered goods")
