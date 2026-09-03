from __future__ import annotations
import re
from uuid import UUID

from packages.extraction.entities.models import Entity
from packages.extraction.relationships.models import Relationship

class GraphRepository:
    def __init__(self, driver) -> None:
        self.driver = driver

    async def add_entity(self, investigation_id: UUID, evidence_id: UUID, entity: Entity) -> None:
        query = """
        MERGE (e:Entity {name: $name, investigation_id: $investigation_id})
        SET e.type = $type,
            e.context = $context,
            e.evidence_id = $evidence_id,
            e.last_updated = timestamp()
        """
        async with self.driver.session() as session:
            await session.run(
                query, 
                name=entity.name, 
                investigation_id=str(investigation_id),
                type=entity.type,
                context=entity.context,
                evidence_id=str(evidence_id)
            )

    async def add_relationship(self, investigation_id: UUID, evidence_id: UUID, rel: Relationship) -> None:
        # Sanitize to prevent Cypher injection
        rel_type = re.sub(r'[^A-Z0-9_]', '', rel.relationship_type.upper())
        if not rel_type:
            rel_type = "RELATED_TO"
            
        query = f"""
        MERGE (s:Entity {{name: $source, investigation_id: $investigation_id}})
        MERGE (t:Entity {{name: $target, investigation_id: $investigation_id}})
        MERGE (s)-[r:{rel_type}]->(t)
        SET r.context = $context,
            r.evidence_id = $evidence_id,
            r.last_updated = timestamp()
        """
        async with self.driver.session() as session:
            await session.run(
                query,
                source=rel.source_entity,
                target=rel.target_entity,
                investigation_id=str(investigation_id),
                context=rel.context,
                evidence_id=str(evidence_id)
            )
