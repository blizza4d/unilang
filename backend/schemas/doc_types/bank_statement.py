from typing import List
from pydantic import BaseModel, ConfigDict, Field


class BankTransaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str = Field(default="", description="Transaction date in YYYY-MM-DD")
    description: str = Field(default="", description="Transaction narrative or counterparty")
    debit: float = Field(default=0.0, description="Debited withdrawal amount")
    credit: float = Field(default=0.0, description="Credited deposit amount")
    balance: float = Field(default=0.0, description="Running account balance")


class ExtractedBankStatement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_holder: str = Field(default="", description="Name of account holder")
    account_number_masked: str = Field(default="", description="Masked account number (e.g. ****1234)")
    bank_name: str = Field(default="", description="Financial institution name")
    period_start: str = Field(default="", description="Statement start date in YYYY-MM-DD")
    period_end: str = Field(default="", description="Statement end date in YYYY-MM-DD")
    currency: str = Field(default="", description="ISO currency code")
    opening_balance: float = Field(default=0.0, description="Starting balance for statement period")
    closing_balance: float = Field(default=0.0, description="Ending balance for statement period")
    transactions: List[BankTransaction] = Field(default_factory=list, description="List of transactions")
