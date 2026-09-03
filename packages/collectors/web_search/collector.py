from __future__ import annotations
from packages.collectors.base.collector import Collector
from packages.collectors.base.errors import CollectorRequestError
from packages.collectors.base.request import CollectionRequest
from packages.collectors.base.result import CollectionResult
from packages.collectors.base.types import CollectorKind, SourceType
from .provider import SearchProvider

class WebSearchCollector(Collector):
    kind = CollectorKind.WEB_SEARCH

    def __init__(self, provider: SearchProvider) -> None:
        self.provider = provider

    async def validate_request(self, request: CollectionRequest) -> None:
        if not request.query:
            raise CollectorRequestError("WebSearchCollector requires a query.")

    async def collect(self, request: CollectionRequest) -> list[CollectionResult]:
        assert request.query is not None
        hits = await self.provider.search(request.query, request.max_results)
        results: list[CollectionResult] = []
        for position, hit in enumerate(hits, start=1):
            results.append(
                CollectionResult(
                    investigation_id=request.investigation_id,
                    collector=self.kind,
                    source_type=SourceType.SEARCH_RESULT,
                    url=hit.url,
                    title=hit.title,
                    content=hit.snippet,
                    metadata={
                        "query": request.query,
                        "rank": hit.rank if hit.rank is not None else position,
                    },
                )
            )
        return results
