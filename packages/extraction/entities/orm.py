from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.shared.db.base import Base

class ExtractedEntityRecord(Base):
    __tablename__ = "extracted_entities"

    entity_record_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investigation_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    evidence_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
