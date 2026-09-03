import asyncio
from uuid import uuid4
from packages.collectors.base.registry import CollectorRegistry
from packages.collectors.base.request import CollectionRequest
from packages.collectors.base.types import CollectorKind
from packages.collectors.http.collector import HTTPCollector
from packages.collectors.web_search.collector import WebSearchCollector
from packages.collectors.web_search.fake_provider import FakeSearchProvider
from packages.evidence.builder import EvidenceBuilder
from packages.evidence.storage.local import LocalEvidenceStorage

async def main() -> None:
    investigation_id = uuid4()
    
    # 1. Setup Registries & Builders
    registry = CollectorRegistry()
    registry.register(WebSearchCollector(provider=FakeSearchProvider()))
    registry.register(HTTPCollector())
    
    storage = LocalEvidenceStorage()
    evidence_builder = EvidenceBuilder(storage=storage)

    print("\n=== 1. SEARCH PIPELINE ===")
    search_results = await registry.get(CollectorKind.WEB_SEARCH).execute(
        CollectionRequest(investigation_id=investigation_id, query="DecentrlAI immutable evidence test")
    )
    print(f"Generated {len(search_results)} search results.")

    print("\n=== 2. COLLECTION & EVIDENCE GENERATION ===")
    for search_hit in search_results:
        if not search_hit.url: continue
        
        # Collect the actual page
        pages = await registry.get(CollectorKind.HTTP).execute(
            CollectionRequest(investigation_id=investigation_id, url=search_hit.url)
        )
        
        # Build immutable evidence
        for page in pages:
            evidence = await evidence_builder.process(page)
            print("\nSUCCESS: Evidence Created!")
            print(f"ID:       {evidence.evidence_id}")
            print(f"URL:      {evidence.original_url}")
            print(f"Hash:     {evidence.content_hash}")
            print(f"Storage:  {evidence.storage_path}")
            print(f"Mime:     {evidence.mime_type}")

if __name__ == "__main__":
    asyncio.run(main())
