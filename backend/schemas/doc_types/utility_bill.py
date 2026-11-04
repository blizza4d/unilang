from typing import List
from pydantic import BaseModel, ConfigDict, Field


class UtilityUsageItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_type: str = Field(default="", description="Electricity, Water, Gas, Internet")
    units_consumed: float = Field(default=0.0, description="Measured units (kWh, m3, GB)")
    rate_per_unit: float = Field(default=0.0, description="Tariff per unit")
    charge_amount: float = Field(default=0.0, description="Total charge for consumption")


class ExtractedUtilityBill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(default="", description="Utility company or provider name")
    account_number_masked: str = Field(default="", description="Masked customer account identifier")
    service_address: str = Field(default="", description="Service premises address")
    billing_period_start: str = Field(default="", description="Billing cycle start in YYYY-MM-DD")
    billing_period_end: str = Field(default="", description="Billing cycle end in YYYY-MM-DD")
    due_date: str = Field(default="", description="Payment due date in YYYY-MM-DD")
    currency: str = Field(default="", description="ISO currency code")
    total_due: float = Field(default=0.0, description="Total amount due for billing cycle")
    usage_items: List[UtilityUsageItem] = Field(default_factory=list, description="Usage breakdown items")
