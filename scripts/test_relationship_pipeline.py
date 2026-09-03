import asyncio
from uuid import uuid4

# Import ORMs to bind them to the declarative Base
import packages.evidence.models.orm
import packages.extraction.entities.orm
import packages.extraction.relationships.orm

from packages.shared.db.session import get_engine, get_sessionmaker, init_models
from packages.extraction.relationships.extractor import AIRelationshipExtractor
from packages.extraction.relationships.postgres import PostgresRelationshipRepository

async def main() -> None:
    investigation_id = uuid4()
    evidence_id = uuid4()

    mock_text = """
    On August 14, 2026, Jane Doe, the CEO of Acme Robotics, announced a major 
    expansion of their manufacturing facilities in Detroit, Michigan. The project, 
    funded by a $50M grant from Global Tech Ventures, will focus on producing 
    the new Sentinel-X autonomous drone systems. Operations are expected to be 
    overseen by Chief Engineer Marcus Vance.
    """

    print("\n=== 1. INITIALIZING DATABASE ===")
    engine = get_engine()
    await init_models(engine)
    session_factory = get_sessionmaker(engine)
    repository = PostgresRelationshipRepository(sessionmaker=session_factory)
    print("Relationship tables initialized.")

    print("\n=== 2. EXTRACTING RELATIONSHIPS WITH OLLAMA ===")
    extractor = AIRelationshipExtractor(model_name="llama3.1")
    result = await extractor.extract(mock_text)
    print(f"Discovered {len(result.relationships)} relationships.")

    print("\n=== 3. PERSISTING TO POSTGRESQL ===")
    await repository.save_extracted_relationships(
        investigation_id=investigation_id,
        evidence_id=evidence_id,
        relationships=result.relationships
    )
    print("Save successful.")

    print("\n=== 4. VERIFYING DATABASE RECORDS ===")
    saved_records = await repository.list_by_investigation(investigation_id)
    
    for record in saved_records:
        print(f"[{record.source_entity}] --({record.relationship_type})--> [{record.target_entity}]")
        print(f"    Evidence ID: {record.evidence_id}")
        print(f"    Context: {record.context}\n")

    await engine.dispose()
    print("=== COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(main())
