"""SQLAlchemy ORM models for QMS ledger persistence."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ComplaintRecord(Base):
    """Persisted complaint row in the QMS ledger (PostgreSQL)."""

    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    complaint_source: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_strength_grade: Mapped[str | None] = mapped_column(String(255), nullable=True)
    batch_lot_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    affected_quantity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    manufacturing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    complaint_type: Mapped[str] = mapped_column(String(255), nullable=False)
    complaint_date: Mapped[date] = mapped_column(Date, nullable=False)
    detailed_complaint_description: Mapped[str] = mapped_column(Text, nullable=False)

    initial_severity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recommended_next_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    ledger_status: Mapped[str] = mapped_column(String(50), nullable=False, default="saved")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
