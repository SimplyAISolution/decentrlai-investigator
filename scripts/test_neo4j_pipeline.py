import asyncio
from uuid import uuid4

from packages.extraction.entities.models import Entity
from packages.extraction.relationships.models import Relationship
from packages.graph.neo4j.connection import Neo4jConnection
from packages.graph.neo4j.repository import GraphRepository

async def main() -> None:
    investigation_id = uuid4()
    evidence_id = uuid4()

    mock_entities = [
        Entity(name="Jane Doe", type="PERSON", context="CEO of Acme Robotics"),
        Entity(name="Acme Robotics", type="ORGANIZATION", context="Expanding facilities in Detroit"),
        Entity(name="Detroit", type="LOCATION", context="Site of new manufacturing facility")
    ]

    mock_relationships = [
        Relationship(source_entity="Jane Doe", target_entity="Acme Robotics", relationship_type="CEO_OF", context="Jane Doe is CEO"),
        Relationship(source_entity="Acme Robotics", target_entity="Detroit", relationship_type="EXPANDING_IN", context="Building new facilities")
    ]

    print("\n=== 1. CONNECTING TO NEO4J ===")
    conn = Neo4jConnection()
    driver = conn.get_driver()
    repo = GraphRepository(driver)

    print("\n=== 2. INGESTING GRAPH DATA ===")
    for entity in mock_entities:
        await repo.add_entity(investigation_id, evidence_id, entity)
        print(f"Added Node: {entity.name}")

    for rel in mock_relationships:
        await repo.add_relationship(investigation_id, evidence_id, rel)
        print(f"Added Edge: [{rel.source_entity}] --({rel.relationship_type})--> [{rel.target_entity}]")

    print("\n=== 3. VERIFYING CYPHER TRAVERSAL ===")
    # Query the graph to find all connections mapped in this investigation
    verify_query = """
    MATCH (s:Entity {investigation_id: $inv_id})-[r]->(t:Entity)
    RETURN s.name AS source, type(r) AS rel_type, t.name AS target, r.context AS context
    """
    async with driver.session() as session:
        result = await session.run(verify_query, inv_id=str(investigation_id))
        records = await result.data()
        
        for record in records:
            print(f"Graph Found: {record['source']} -[{record['rel_type']}]-> {record['target']} (Context: {record['context']})")

    await conn.close()
    print("\n=== COMPLETE: Neo4j mapping successful ===")

if __name__ == "__main__":
    asyncio.run(main())
