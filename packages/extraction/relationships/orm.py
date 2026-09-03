from __future__ import annotations
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.shared.db.base import Base

class ExtractedRelationshipRecord(Base):
    __tablename__ = "extracted_relationships"

    relationship_record_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    investigation_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    evidence_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    
    source_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    target_entity: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    
    extracted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
