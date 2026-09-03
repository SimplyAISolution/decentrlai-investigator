import asyncio
from uuid import uuid4
from packages.collectors.base.registry import CollectorRegistry
from packages.collectors.base.request import CollectionRequest
from packages.collectors.base.types import CollectorKind
from packages.collectors.http.collector import HTTPCollector
from packages.collectors.web_search.collector import WebSearchCollector
from packages.collectors.web_search.fake_provider import FakeSearchProvider

async def main() -> None:
    investigation_id = uuid4()
    registry = CollectorRegistry()
    search_collector = WebSearchCollector(provider=FakeSearchProvider())
    http_collector = HTTPCollector()
    
    registry.register(search_collector)
    registry.register(http_collector)

    print("\n=== REGISTERED ===")
    for kind in registry.available():
        print(kind.value)

    print("\n=== SEARCH ===")
    search_results = await registry.get(CollectorKind.WEB_SEARCH).execute(
        CollectionRequest(investigation_id=investigation_id, query="DecentrlAI test investigation", max_results=5)
    )
    for result in search_results:
        print(result.as_dict())

    print("\n=== COLLECT ===")
    for search_result in search_results:
        if not search_result.url:
            continue
        pages = await registry.get(CollectorKind.HTTP).execute(
            CollectionRequest(investigation_id=investigation_id, url=search_result.url)
        )
        for page in pages:
            print({
                "url": page.url,
                "collector": page.collector.value,
                "status": page.metadata.get("http_status"),
                "bytes": page.metadata.get("content_length"),
            })

if __name__ == "__main__":
    asyncio.run(main())
