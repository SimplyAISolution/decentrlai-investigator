import json
import logging
from uuid import UUID

from packages.collectors.base.request import CollectionRequest
from packages.collectors.base.types import CollectorKind
from packages.evidence.builder import EvidenceBuilder
from packages.evidence.repository.postgres import PostgresEvidenceRepository
from packages.extraction.text.html import HTMLExtractor
from packages.extraction.entities.extractor import AIEntityExtractor
from packages.extraction.entities.postgres import PostgresEntityRepository
from packages.extraction.relationships.extractor import AIRelationshipExtractor
from packages.extraction.relationships.postgres import PostgresRelationshipRepository
from packages.graph.neo4j.repository import GraphRepository

logger = logging.getLogger(__name__)

async def publish_event(ctx, investigation_id: UUID, step: str, message: str, data: dict | None = None) -> None:
    channel = f"channel:investigation:{investigation_id}"
    payload = {
        "investigation_id": str(investigation_id),
        "step": step,
        "message": message,
        "data": data or {},
    }
    if "redis" in ctx:
        await ctx["redis"].publish(channel, json.dumps(payload))

async def run_autonomous_investigation(ctx, investigation_id: UUID, target_query: str) -> str:
    logger.info(f"Starting investigation {investigation_id} for target: {target_query}")
    await publish_event(ctx, investigation_id, "STARTED", f"Investigation launched for query: {target_query}")
    
    # 1. Retrieve persistent resources from context
    registry = ctx["registry"]
    storage = ctx["storage"]
    postgres_session = ctx["postgres_session"]
    neo4j_driver = ctx["neo4j_driver"]

    evidence_builder = EvidenceBuilder(storage=storage)
    html_extractor = HTMLExtractor()
    entity_extractor = AIEntityExtractor(model_name="llama3.1")
    rel_extractor = AIRelationshipExtractor(model_name="llama3.1")
    
    evidence_repo = PostgresEvidenceRepository(postgres_session)
    entity_repo = PostgresEntityRepository(postgres_session)
    rel_repo = PostgresRelationshipRepository(postgres_session)
    graph_repo = GraphRepository(neo4j_driver)

    # 2. Search Discovery
    await publish_event(ctx, investigation_id, "SEARCHING", f"Executing web search for target...")
    search_hits = await registry.get(CollectorKind.WEB_SEARCH).execute(
        CollectionRequest(investigation_id=investigation_id, query=target_query, max_results=2)
    )
    await publish_event(ctx, investigation_id, "SEARCH_COMPLETE", f"Discovered {len(search_hits)} candidate sources")

    # 3. Collection & Extraction Loop
    for hit in search_hits:
        if not hit.url:
            continue
        try:
            await publish_event(ctx, investigation_id, "COLLECTING", f"Retrieving: {hit.url}")
            pages = await registry.get(CollectorKind.HTTP).execute(
                CollectionRequest(investigation_id=investigation_id, url=hit.url)
            )
            for page in pages:
                # Evidence hashing and CAS persistence
                evidence = await evidence_builder.process(page)
                await evidence_repo.save(evidence)
                await publish_event(
                    ctx, 
                    investigation_id, 
                    "EVIDENCE_STORED", 
                    f"Saved immutable evidence ({evidence.content_hash[:8]}...)",
                    {"evidence_id": str(evidence.evidence_id), "hash": evidence.content_hash}
                )

                # Extract cleaned text
                raw_bytes = await storage.retrieve(evidence.storage_path)
                doc = html_extractor.extract(evidence, raw_bytes)
                if not doc.clean_text:
                    continue

                # Local LLM Extraction
                await publish_event(ctx, investigation_id, "EXTRACTING", f"Running Ollama extraction on {hit.url[:45]}...")
                entities_result = await entity_extractor.extract(doc.clean_text)
                rels_result = await rel_extractor.extract(doc.clean_text)

                # Postgres Persistence
                await entity_repo.save_extracted_entities(investigation_id, evidence.evidence_id, entities_result.entities)
                await rel_repo.save_extracted_relationships(investigation_id, evidence.evidence_id, rels_result.relationships)

                # Neo4j Ingestion
                for entity in entities_result.entities:
                    await graph_repo.add_entity(investigation_id, evidence.evidence_id, entity)
                for rel in rels_result.relationships:
                    await graph_repo.add_relationship(investigation_id, evidence.evidence_id, rel)

                await publish_event(
                    ctx,
                    investigation_id,
                    "GRAPH_UPDATED",
                    f"Pushed {len(entities_result.entities)} entities and {len(rels_result.relationships)} relationships to Neo4j",
                    {"entities": len(entities_result.entities), "relationships": len(rels_result.relationships)}
                )

        except Exception as e:
            logger.error(f"Failed to process {hit.url}: {e}")
            await publish_event(ctx, investigation_id, "ERROR", f"Error on {hit.url}: {str(e)}")

    await publish_event(ctx, investigation_id, "COMPLETE", "Autonomous investigation workflow finished successfully")
    return "SUCCESS"
