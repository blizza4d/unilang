from pydantic import BaseModel, ConfigDict, Field


class ExtractedIDDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_type: str = Field(default="", description="Passport, National ID, Driving License, Residence Permit")
    issuing_country: str = Field(default="", description="ISO 3166-1 alpha-3 issuing country code")
    full_name: str = Field(default="", description="Full legal name of the document holder")
    date_of_birth: str = Field(default="", description="Birth date in YYYY-MM-DD")
    document_number_masked: str = Field(default="", description="Masked document number (e.g. *******1234)")
    expiry_date: str = Field(default="", description="Document expiry date in YYYY-MM-DD")
