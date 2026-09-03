import asyncio
from uuid import UUID

from packages.extraction.entities.models import Entity
from packages.extraction.relationships.models import Relationship
from packages.graph.neo4j.connection import Neo4jConnection
from packages.graph.neo4j.repository import GraphRepository

async def main() -> None:
    # Use a fixed UUID so the frontend knows exactly what to query
    fixed_inv_id = UUID("00000000-0000-0000-0000-000000000001")
    fixed_ev_id = UUID("00000000-0000-0000-0000-000000000002")

    entities = [
        Entity(name="Jane Doe", type="PERSON", context="CEO of Acme Robotics"),
        Entity(name="Acme Robotics", type="ORGANIZATION", context="Expanding facilities"),
        Entity(name="Global Tech Ventures", type="ORGANIZATION", context="Funder"),
        Entity(name="Detroit", type="LOCATION", context="Manufacturing site"),
        Entity(name="Sentinel-X", type="PRODUCT", context="Autonomous drone")
    ]

    relationships = [
        Relationship(source_entity="Jane Doe", target_entity="Acme Robotics", relationship_type="CEO_OF", context=""),
        Relationship(source_entity="Acme Robotics", target_entity="Detroit", relationship_type="EXPANDING_IN", context=""),
        Relationship(source_entity="Global Tech Ventures", target_entity="Acme Robotics", relationship_type="FUNDED", context=""),
        Relationship(source_entity="Acme Robotics", target_entity="Sentinel-X", relationship_type="MANUFACTURES", context="")
    ]

    conn = Neo4jConnection()
    repo = GraphRepository(conn.get_driver())

    print("\nSeeding predictable demo graph into Neo4j...")
    for entity in entities:
        await repo.add_entity(fixed_inv_id, fixed_ev_id, entity)
    for rel in relationships:
        await repo.add_relationship(fixed_inv_id, fixed_ev_id, rel)
    
    await conn.close()
    print("Seed complete! Target ID: 00000000-0000-0000-0000-000000000001")

if __name__ == "__main__":
    asyncio.run(main())
