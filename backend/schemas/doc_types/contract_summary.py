from typing import List
from pydantic import BaseModel, ConfigDict, Field


class ExtractedContractSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parties: List[str] = Field(default_factory=list, description="Names of legal contracting parties")
    effective_date: str = Field(default="", description="Agreement effective start date in YYYY-MM-DD")
    term_months: int = Field(default=12, description="Duration of contract term in months")
    renewal_terms: str = Field(default="", description="Renewal terms: Auto-renew, Manual, Non-renewable")
    total_value: float = Field(default=0.0, description="Total contract aggregate value")
    currency: str = Field(default="", description="ISO currency code")
    governing_law: str = Field(default="", description="Governing law jurisdiction or state")
    termination_notice_days: int = Field(default=30, description="Required days of written notice for termination")
