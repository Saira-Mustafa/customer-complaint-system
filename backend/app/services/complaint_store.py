"""Temporary in-memory complaint storage shared by API routes and AI tools."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional
from uuid import UUID, uuid4

from app.schemas.complaint import Complaint, ComplaintCreate, ComplaintUpdate

# Temporary in-memory storage (no database yet)
complaints_db: dict[UUID, Complaint] = {}


def list_complaints() -> list[Complaint]:
    return list(complaints_db.values())


def get_complaint(complaint_id: UUID) -> Optional[Complaint]:
    return complaints_db.get(complaint_id)


def create_complaint(complaint: ComplaintCreate) -> Complaint:
    new_complaint = Complaint(id=uuid4(), **complaint.model_dump())
    complaints_db[new_complaint.id] = new_complaint
    return new_complaint


def create_complaint_from_extracted(data: dict[str, Any]) -> Complaint:
    """Create a complaint from AI-extracted fields.

    Fills only non-pharmaceutical defaults for required schema fields.
    Does not invent batch numbers, dates, quantities, or product facts.
    """
    create_data = ComplaintCreate(
        complaint_source=data.get("complaint_source") or "Customer Report",
        customer_name=data.get("customer_name") or "Unspecified",
        product_name=data.get("product_name") or "Unspecified",
        product_strength_grade=data.get("product_strength_grade"),
        batch_lot_number=data.get("batch_lot_number"),
        affected_quantity=data.get("affected_quantity"),
        manufacturing_date=data.get("manufacturing_date"),
        expiry_date=data.get("expiry_date"),
        complaint_type=data.get("complaint_type") or "Unspecified",
        complaint_date=data.get("complaint_date") or date.today(),
        detailed_complaint_description=(
            data.get("detailed_complaint_description") or "No description provided."
        ),
        initial_severity=data.get("initial_severity"),
        priority=data.get("priority"),
    )
    return create_complaint(create_data)


def update_complaint(complaint_id: UUID, updates: ComplaintUpdate) -> Complaint:
    existing = complaints_db.get(complaint_id)
    if existing is None:
        raise KeyError(f"Complaint not found: {complaint_id}")

    updated_data = existing.model_dump()
    updated_data.update(updates.model_dump(exclude_unset=True))
    updated_complaint = Complaint(**updated_data)
    complaints_db[complaint_id] = updated_complaint
    return updated_complaint
