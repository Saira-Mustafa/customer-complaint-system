"""LangGraph tools for logging and editing complaints."""

from __future__ import annotations

import json
from datetime import date
from typing import Any, Optional
from uuid import UUID

from langchain_core.tools import tool

from app.schemas.complaint import Complaint, ComplaintExtraction
from app.services import complaint_store


def _json(data: dict) -> str:
    return json.dumps(data, default=str)


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def log_complaint_from_fields(
    *,
    complaint_source: Optional[str] = None,
    customer_name: Optional[str] = None,
    product_name: Optional[str] = None,
    product_strength_grade: Optional[str] = None,
    batch_lot_number: Optional[str] = None,
    affected_quantity: Optional[str] = None,
    manufacturing_date: Optional[str | date] = None,
    expiry_date: Optional[str | date] = None,
    complaint_type: Optional[str] = None,
    complaint_date: Optional[str | date] = None,
    detailed_complaint_description: Optional[str] = None,
    initial_severity: Optional[str] = None,
    priority: Optional[str] = None,
) -> Complaint:
    """Shared create logic used by the log_complaint tool and document workflow."""
    if not product_name and not detailed_complaint_description and not customer_name:
        raise ValueError(
            "Not enough information to log a complaint. "
            "Please provide at least the customer, product, or a description."
        )

    def as_date(value: Optional[str | date]) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, date):
            return value
        return _parse_date(value)

    return complaint_store.create_complaint_from_extracted(
        {
            "complaint_source": complaint_source,
            "customer_name": customer_name,
            "product_name": product_name,
            "product_strength_grade": product_strength_grade,
            "batch_lot_number": batch_lot_number,
            "affected_quantity": affected_quantity,
            "manufacturing_date": as_date(manufacturing_date),
            "expiry_date": as_date(expiry_date),
            "complaint_type": complaint_type,
            "complaint_date": as_date(complaint_date),
            "detailed_complaint_description": detailed_complaint_description,
            "initial_severity": initial_severity,
            "priority": priority,
        }
    )


def log_complaint_from_extraction(extracted: ComplaintExtraction) -> Complaint:
    """Log a complaint from a Pydantic extraction result (document workflow)."""
    data: dict[str, Any] = extracted.model_dump(exclude_none=True)
    return log_complaint_from_fields(**data)


@tool
def log_complaint(
    complaint_source: Optional[str] = None,
    customer_name: Optional[str] = None,
    product_name: Optional[str] = None,
    product_strength_grade: Optional[str] = None,
    batch_lot_number: Optional[str] = None,
    affected_quantity: Optional[str] = None,
    manufacturing_date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    complaint_type: Optional[str] = None,
    complaint_date: Optional[str] = None,
    detailed_complaint_description: Optional[str] = None,
) -> str:
    """Log a NEW customer complaint into the system.

    Use this when the user wants to create or report a new complaint.
    Only include fields that are clearly present in the user's message.
    Do NOT invent batch numbers, quantities, manufacturing dates, or expiry dates.
    Leave unknown fields omitted/null.
    """
    try:
        complaint = log_complaint_from_fields(
            complaint_source=complaint_source,
            customer_name=customer_name,
            product_name=product_name,
            product_strength_grade=product_strength_grade,
            batch_lot_number=batch_lot_number,
            affected_quantity=affected_quantity,
            manufacturing_date=manufacturing_date,
            expiry_date=expiry_date,
            complaint_type=complaint_type,
            complaint_date=complaint_date,
            detailed_complaint_description=detailed_complaint_description,
        )
    except ValueError as exc:
        return _json({"status": "error", "message": str(exc)})

    return _json(
        {
            "status": "success",
            "action": "log_complaint",
            "complaint_id": str(complaint.id),
            "complaint": complaint.model_dump(mode="json"),
        }
    )


@tool
def edit_complaint(
    complaint_id: str,
    complaint_source: Optional[str] = None,
    customer_name: Optional[str] = None,
    product_name: Optional[str] = None,
    product_strength_grade: Optional[str] = None,
    batch_lot_number: Optional[str] = None,
    affected_quantity: Optional[str] = None,
    manufacturing_date: Optional[str] = None,
    expiry_date: Optional[str] = None,
    complaint_type: Optional[str] = None,
    complaint_date: Optional[str] = None,
    detailed_complaint_description: Optional[str] = None,
    initial_severity: Optional[str] = None,
    priority: Optional[str] = None,
) -> str:
    """Edit an EXISTING complaint by ID. Update ONLY the fields the user wants changed.

    Use this when the user corrects or updates an existing complaint.
    You MUST have a real complaint_id. Never invent a complaint_id.
    Fields that are not supplied are left unchanged so existing data is preserved.
    """
    if not complaint_id or not complaint_id.strip():
        return _json(
            {
                "status": "needs_clarification",
                "message": (
                    "A complaint_id is required to edit a complaint. "
                    "Please provide the complaint ID."
                ),
            }
        )

    try:
        cid = UUID(complaint_id.strip())
    except ValueError:
        return _json(
            {
                "status": "error",
                "message": f"Invalid complaint_id format: {complaint_id}",
            }
        )

    if complaint_store.get_complaint(cid) is None:
        return _json(
            {
                "status": "error",
                "message": f"Complaint not found for id: {complaint_id}",
            }
        )

    raw_updates = {
        "complaint_source": complaint_source,
        "customer_name": customer_name,
        "product_name": product_name,
        "product_strength_grade": product_strength_grade,
        "batch_lot_number": batch_lot_number,
        "affected_quantity": affected_quantity,
        "manufacturing_date": _parse_date(manufacturing_date),
        "expiry_date": _parse_date(expiry_date),
        "complaint_type": complaint_type,
        "complaint_date": _parse_date(complaint_date),
        "detailed_complaint_description": detailed_complaint_description,
        "initial_severity": initial_severity,
        "priority": priority,
    }

    provided = {
        key: value
        for key, value in raw_updates.items()
        if value is not None and not (isinstance(value, str) and not value.strip())
    }

    if not provided:
        return _json(
            {
                "status": "needs_clarification",
                "message": "No fields to update were provided. What should be changed?",
            }
        )

    from app.schemas.complaint import ComplaintUpdate

    updated = complaint_store.update_complaint(cid, ComplaintUpdate(**provided))

    return _json(
        {
            "status": "success",
            "action": "edit_complaint",
            "complaint_id": str(updated.id),
            "complaint": updated.model_dump(mode="json"),
        }
    )


COMPLAINT_TOOLS = [log_complaint, edit_complaint]
