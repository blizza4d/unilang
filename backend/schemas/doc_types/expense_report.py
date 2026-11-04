from typing import List
from pydantic import BaseModel, ConfigDict, Field


class ExpenseEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str = Field(default="", description="Expense date in YYYY-MM-DD")
    category: str = Field(default="", description="Category: Travel, Meals, Lodging, Supplies, Software")
    merchant: str = Field(default="", description="Merchant name")
    amount: float = Field(default=0.0, description="Expense amount")


class ExtractedExpenseReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    employee: str = Field(default="", description="Employee name or submitter identifier")
    period: str = Field(default="", description="Expense reporting period or month")
    currency: str = Field(default="", description="ISO currency code")
    total_amount: float = Field(default=0.0, description="Grand total reimbursable expenses")
    expenses: List[ExpenseEntry] = Field(default_factory=list, description="Itemized expense entries")
