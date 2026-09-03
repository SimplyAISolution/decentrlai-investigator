from __future__ import annotations
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from packages.extraction.relationships.models import Relationship
from packages.extraction.relationships.orm import ExtractedRelationshipRecord

class PostgresRelationshipRepository:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self.sessionmaker = sessionmaker

    async def save_extracted_relationships(
        self, 
        investigation_id: UUID, 
        evidence_id: UUID, 
        relationships: list[Relationship]
    ) -> None:
        if not relationships:
            return

        records = [
            ExtractedRelationshipRecord(
                investigation_id=investigation_id,
                evidence_id=evidence_id,
                source_entity=rel.source_entity,
                target_entity=rel.target_entity,
                relationship_type=rel.relationship_type,
                context=rel.context,
            )
            for rel in relationships
        ]

        async with self.sessionmaker() as session:
            async with session.begin():
                session.add_all(records)

    async def list_by_investigation(self, investigation_id: UUID) -> list[ExtractedRelationshipRecord]:
        async with self.sessionmaker() as session:
            stmt = select(ExtractedRelationshipRecord).where(
                ExtractedRelationshipRecord.investigation_id == investigation_id
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
