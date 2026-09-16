"""Pydantic models for customer complaints."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ComplaintBase(BaseModel):
    """Shared complaint fields from the assignment/demo form."""

    # Origin & Customer Details
    complaint_source: str = Field(..., description="Where the complaint came from")
    customer_name: str

    # Product & Batch Identification
    product_name: str
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None

    # Complaint Details
    complaint_type: str
    complaint_date: date
    detailed_complaint_description: str

    # Initial Assessment (often set after first review)
    initial_severity: Optional[str] = None
    priority: Optional[str] = None
    recommended_next_action: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    """Request body for creating a new complaint (POST /complaints)."""

    pass


class ComplaintExtraction(BaseModel):
    """Structured complaint fields extracted by the AI.

    Every field is optional because the AI must only fill values that are
    clearly present in the user's message — never invent missing details.
    """

    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    product_strength_grade: Optional[str] = None
    batch_lot_number: Optional[str] = None
    affected_quantity: Optional[str] = None
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None
    complaint_type: Optional[str] = None
    complaint_date: Optional[date] = None
    detailed_complaint_description: Optional[str] = None
    initial_severity: Optional[str] = None
    priority: Optional[str] = None
    recommended_next_action: Optional[str] = None


class ComplaintUpdate(ComplaintExtraction):
    """Request body for partial updates (PATCH /complaints/{complaint_id}).

    Reuses ComplaintExtraction so every field stays optional.
    """

    pass


class Complaint(ComplaintBase):
    """Full complaint returned by the API, including a generated id."""

    id: UUID


class InitialRiskAssessment(BaseModel):
    """AI-recommended INITIAL risk assessment (not a final QA decision)."""

    initial_severity: Optional[str] = None
    priority: Optional[str] = None
    recommended_next_action: Optional[str] = None
    label: str = (
        "AI-recommended initial assessment (not a final pharmaceutical QA decision)"
    )


class AIComplaintRequest(BaseModel):
    """Request body for POST /ai/complaint."""

    message: str = Field(..., min_length=1, description="Natural-language complaint text")
    complaint_id: Optional[UUID] = Field(
        default=None,
        description="Optional ID when correcting an existing complaint",
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message cannot be empty or only whitespace")
        return cleaned


class AgentComplaintResult(BaseModel):
    """Internal/agent result used to build the API response."""

    action: Optional[str] = None
    complaint_id: Optional[UUID] = None
    complaint: Optional[Complaint] = None
    risk_assessment: Optional[InitialRiskAssessment] = None
    clarification: Optional[str] = None
    assistant_message: Optional[str] = None


class AIComplaintResponse(BaseModel):
    """Response from POST /ai/complaint (agent with tools)."""

    message: str
    action: Optional[str] = None
    complaint_id: Optional[UUID] = None
    complaint: Optional[Complaint] = None
    risk_assessment: Optional[InitialRiskAssessment] = None
    clarification: Optional[str] = None
    assistant_message: Optional[str] = None


class DocumentComplaintResult(BaseModel):
    """Internal result from the PDF document extraction pipeline."""

    action: str = "document_extraction"
    complaint_id: UUID
    complaint: Complaint
    risk_assessment: InitialRiskAssessment
    extracted_text: str
    extracted_complaint: ComplaintExtraction


class DocumentComplaintResponse(BaseModel):
    """Response from POST /ai/complaint/document."""

    action: str = "document_extraction"
    complaint_id: UUID
    complaint: Complaint
    risk_assessment: InitialRiskAssessment
    filename: Optional[str] = None
    extracted_text: Optional[str] = None
    extracted_complaint: Optional[ComplaintExtraction] = None


class LedgerSaveRequest(BaseModel):
    """Optional body when saving a working complaint to the QMS ledger."""

    recommended_next_action: Optional[str] = None


class LedgerSaveResponse(BaseModel):
    """Response from POST /complaints/{complaint_id}/ledger."""

    complaint: Complaint
    ledger_status: str
    message: str
