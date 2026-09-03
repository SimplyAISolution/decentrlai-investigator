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

from packages.extraction.text.html import HTMLExtractor

async def main() -> None:
    investigation_id = uuid4()
    
    # Setup Subsystems
    registry = CollectorRegistry()
    registry.register(WebSearchCollector(provider=FakeSearchProvider()))
    registry.register(HTTPCollector())
    
    storage = LocalEvidenceStorage()
    evidence_builder = EvidenceBuilder(storage=storage)
    extractor = HTMLExtractor()

    print("\n=== 1. COLLECT & STORE EVIDENCE ===")
    search_hits = await registry.get(CollectorKind.WEB_SEARCH).execute(
        CollectionRequest(investigation_id=investigation_id, query="Test extraction")
    )
    
    for hit in search_hits:
        if not hit.url: continue
        pages = await registry.get(CollectorKind.HTTP).execute(
            CollectionRequest(investigation_id=investigation_id, url=hit.url)
        )
        
        for page in pages:
            # Generate Immutable Evidence
            evidence = await evidence_builder.process(page)
            print(f"Stored Evidence: {evidence.evidence_id} (URL: {evidence.original_url})")

            # Retrieve bytes directly from immutable storage
            raw_bytes = await storage.retrieve(evidence.storage_path)

            print("\n=== 2. TEXT EXTRACTION ===")
            doc = extractor.extract(evidence, raw_bytes)
            
            print(f"Title:       {doc.title}")
            print(f"Text Hash:   {doc.text_hash}")
            print(f"Clean Chars: {len(doc.clean_text)}")
            print(f"Metadata:    {len(doc.metadata)} tags found")
            
            # Show a snippet of the cleaned text
            snippet = doc.clean_text[:150].replace('\n', ' ') + "..." if doc.clean_text else "No text found."
            print(f"\nSnippet:     {snippet}")

if __name__ == "__main__":
    asyncio.run(main())
