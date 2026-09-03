from __future__ import annotations
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from packages.extraction.entities.models import Entity
from packages.extraction.entities.orm import ExtractedEntityRecord

class PostgresEntityRepository:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.sessionmaker = sessionmaker

    async def save_extracted_entities(
        self, 
        investigation_id: UUID, 
        evidence_id: UUID, 
        entities: list[Entity]
    ) -> None:
        """Bulk inserts a list of AI-extracted entities."""
        if not entities:
            return

        records = [
            ExtractedEntityRecord(
                investigation_id=investigation_id,
                evidence_id=evidence_id,
                name=entity.name,
                entity_type=entity.type,
                context=entity.context,
            )
            for entity in entities
        ]

        async with self.sessionmaker() as session:
            async with session.begin():
                session.add_all(records)

    async def list_by_investigation(self, investigation_id: UUID) -> list[ExtractedEntityRecord]:
        """Retrieves all entities discovered during an investigation."""
        async with self.sessionmaker() as session:
            stmt = select(ExtractedEntityRecord).where(
                ExtractedEntityRecord.investigation_id == investigation_id
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
