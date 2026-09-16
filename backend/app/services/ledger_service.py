"""Persist working (in-memory) complaints into the PostgreSQL QMS ledger."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.complaint import ComplaintRecord
from app.schemas.complaint import Complaint, LedgerSaveResponse
from app.services import complaint_store


def _record_to_complaint(record: ComplaintRecord) -> Complaint:
    return Complaint(
        id=record.id,
        complaint_source=record.complaint_source,
        customer_name=record.customer_name,
        product_name=record.product_name,
        product_strength_grade=record.product_strength_grade,
        batch_lot_number=record.batch_lot_number,
        affected_quantity=record.affected_quantity,
        manufacturing_date=record.manufacturing_date,
        expiry_date=record.expiry_date,
        complaint_type=record.complaint_type,
        complaint_date=record.complaint_date,
        detailed_complaint_description=record.detailed_complaint_description,
        initial_severity=record.initial_severity,
        priority=record.priority,
        recommended_next_action=record.recommended_next_action,
    )


def list_ledger_complaints(db: Session) -> list[Complaint]:
    records = db.query(ComplaintRecord).order_by(ComplaintRecord.updated_at.desc()).all()
    return [_record_to_complaint(record) for record in records]


def get_ledger_complaint(db: Session, complaint_id: UUID) -> Complaint | None:
    record = db.get(ComplaintRecord, complaint_id)
    if record is None:
        return None
    return _record_to_complaint(record)


def save_complaint_to_ledger(
    db: Session,
    complaint_id: UUID,
    *,
    recommended_next_action: str | None = None,
) -> LedgerSaveResponse:
    """Upsert the current working complaint into PostgreSQL.

    AI working state remains in-memory until the user explicitly saves.
    """
    working = complaint_store.get_complaint(complaint_id)
    if working is None:
        # Allow re-saving from ledger itself if still present in DB
        existing = db.get(ComplaintRecord, complaint_id)
        if existing is None:
            raise KeyError(f"Complaint not found: {complaint_id}")
        return LedgerSaveResponse(
            complaint=_record_to_complaint(existing),
            ledger_status=existing.ledger_status or "saved",
            message="Complaint already present in QMS Ledger.",
        )

    action = recommended_next_action
    if action is None:
        action = getattr(working, "recommended_next_action", None)

    existing = db.get(ComplaintRecord, complaint_id)
    if existing is None:
        record = ComplaintRecord(
            id=working.id,
            complaint_source=working.complaint_source,
            customer_name=working.customer_name,
            product_name=working.product_name,
            product_strength_grade=working.product_strength_grade,
            batch_lot_number=working.batch_lot_number,
            affected_quantity=working.affected_quantity,
            manufacturing_date=working.manufacturing_date,
            expiry_date=working.expiry_date,
            complaint_type=working.complaint_type,
            complaint_date=working.complaint_date,
            detailed_complaint_description=working.detailed_complaint_description,
            initial_severity=working.initial_severity,
            priority=working.priority,
            recommended_next_action=action,
            ledger_status="saved",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return LedgerSaveResponse(
            complaint=_record_to_complaint(record),
            ledger_status="saved",
            message="Complaint saved to QMS Ledger.",
        )

    # Update existing row — no duplicate insert
    existing.complaint_source = working.complaint_source
    existing.customer_name = working.customer_name
    existing.product_name = working.product_name
    existing.product_strength_grade = working.product_strength_grade
    existing.batch_lot_number = working.batch_lot_number
    existing.affected_quantity = working.affected_quantity
    existing.manufacturing_date = working.manufacturing_date
    existing.expiry_date = working.expiry_date
    existing.complaint_type = working.complaint_type
    existing.complaint_date = working.complaint_date
    existing.detailed_complaint_description = working.detailed_complaint_description
    existing.initial_severity = working.initial_severity
    existing.priority = working.priority
    existing.recommended_next_action = action
    existing.ledger_status = "saved"
    db.commit()
    db.refresh(existing)

    return LedgerSaveResponse(
        complaint=_record_to_complaint(existing),
        ledger_status="saved",
        message="Complaint updated in QMS Ledger.",
    )
