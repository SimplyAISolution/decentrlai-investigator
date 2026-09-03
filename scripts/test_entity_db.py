import asyncio
from uuid import uuid4

# Import ORMs so they are registered with the Base metadata
import packages.evidence.models.orm
import packages.extraction.entities.orm

from packages.shared.db.session import get_engine, get_sessionmaker, init_models
from packages.extraction.entities.models import Entity
from packages.extraction.entities.postgres import PostgresEntityRepository

async def main() -> None:
    investigation_id = uuid4()
    evidence_id = uuid4()

    print("\n=== 1. DATABASE CONNECTION & SCHEMA INIT ===")
    engine = get_engine()
    await init_models(engine)
    session_factory = get_sessionmaker(engine)
    repository = PostgresEntityRepository(sessionmaker=session_factory)
    print("Entity tables initialized successfully.")

    print("\n=== 2. SIMULATING AI EXTRACTION OUTPUT ===")
    mock_ai_output = [
        Entity(name="Jane Doe", type="PERSON", context="CEO of Acme Robotics"),
        Entity(name="Acme Robotics", type="ORGANIZATION", context="Expanding facilities in Detroit"),
        Entity(name="Detroit", type="LOCATION", context="Site of new manufacturing facility")
    ]
    
    print(f"Saving {len(mock_ai_output)} entities to PostgreSQL...")
    await repository.save_extracted_entities(
        investigation_id=investigation_id,
        evidence_id=evidence_id,
        entities=mock_ai_output
    )

    print("\n=== 3. VERIFYING DATABASE RECORDS ===")
    saved_records = await repository.list_by_investigation(investigation_id)
    
    for record in saved_records:
        print(f"[{record.entity_type}] {record.name}")
        print(f"    Source Evidence: {record.evidence_id}")
        print(f"    Context: {record.context}\n")

    await engine.dispose()
    print("=== COMPLETE: Entity persistence verified ===")

if __name__ == "__main__":
    asyncio.run(main())
