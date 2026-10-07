import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models import JobStatus, RecipientStatus

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class RecipientInput(BaseModel):
    name: str = Field(..., min_length=1, description="Recipient's full name", json_schema_extra={"example": "Alice Johnson"})
    email: str = Field(..., description="Recipient's email address", json_schema_extra={"example": "alice@example.com"})
    custom_text: Optional[str] = Field(None, description="Optional custom text (e.g., Honors, Grade)", json_schema_extra={"example": "Passed with Distinction"})

    @field_validator("name")
    def name_must_not_be_blank(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Recipient name cannot be empty or whitespace only.")
        return v_stripped

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        v_stripped = v.strip()
        if not EMAIL_REGEX.match(v_stripped):
            raise ValueError(f"Invalid email address format: '{v}'")
        return v_stripped

class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, description="Certificate / Course Title", json_schema_extra={"example": "Full Stack Engineering"})
    issuer: str = Field(..., min_length=2, description="Issuing Organization", json_schema_extra={"example": "Acme Learning Institute"})
    issue_date: Optional[str] = Field(None, description="Issue date text", json_schema_extra={"example": "October 7, 2026"})
    signatory_name: Optional[str] = Field("Dr. Alex Vance", description="Name of the authorized signatory", json_schema_extra={"example": "Dr. Alex Vance"})
    signatory_title: Optional[str] = Field("Director of Certification", description="Title of the authorized signatory", json_schema_extra={"example": "Director of Certification"})
    recipients: List[RecipientInput] = Field(..., min_length=1, description="List of recipient details")
    format: Optional[str] = Field("pdf", description="Output format: 'pdf' or 'png'")

    @field_validator("format")
    def validate_format(cls, v: str) -> str:
        v_lower = v.lower()
        if v_lower not in ("pdf", "png"):
            raise ValueError("Format must be either 'pdf' or 'png'.")
        return v_lower

class RecipientOutput(BaseModel):
    id: str
    recipient_name: str
    recipient_email: str
    custom_text: Optional[str] = None
    status: RecipientStatus
    error_message: Optional[str] = None
    download_url: Optional[str] = None
    verify_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id: str
    title: str
    issuer: str
    issue_date: str
    signatory_name: Optional[str] = None
    signatory_title: Optional[str] = None
    status: JobStatus
    total_recipients: int
    processed_count: int
    success_count: int
    failure_count: int
    progress_percentage: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    recipients: List[RecipientOutput] = []
    zip_download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class VerificationResponse(BaseModel):
    valid: bool
    certificate_id: str
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    title: Optional[str] = None
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    custom_text: Optional[str] = None
    created_at: Optional[datetime] = None
    verification_message: str
