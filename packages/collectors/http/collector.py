from __future__ import annotations
import httpx
from packages.collectors.base.collector import Collector
from packages.collectors.base.errors import CollectorNetworkError, CollectorRequestError
from packages.collectors.base.request import CollectionRequest
from packages.collectors.base.result import CollectionResult
from packages.collectors.base.types import CollectorKind, SourceType
from .security import resolve_and_validate_host, validate_url

class HTTPCollector(Collector):
    kind = CollectorKind.HTTP

    def __init__(self, *, user_agent: str = "DecentrlAI-Collector/0.1", max_bytes: int = 5_000_000) -> None:
        self.user_agent = user_agent
        self.max_bytes = max_bytes

    async def validate_request(self, request: CollectionRequest) -> None:
        if not request.url:
            raise CollectorRequestError("HTTPCollector requires a URL.")
        validate_url(request.url)
        parsed = httpx.URL(request.url)
        if parsed.host is None:
            raise CollectorRequestError("URL contains no hostname.")
        await resolve_and_validate_host(parsed.host)

    async def collect(self, request: CollectionRequest) -> list[CollectionResult]:
        assert request.url is not None
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.5",
        }
        try:
            async with httpx.AsyncClient(timeout=request.timeout_seconds, follow_redirects=False, headers=headers) as client:
                response = await client.get(request.url)
        except httpx.HTTPError as exc:
            raise CollectorNetworkError(str(exc)) from exc

        content = response.content
        if len(content) > self.max_bytes:
            content = content[: self.max_bytes]
        content_type = response.headers.get("content-type", "")

        result = CollectionResult(
            investigation_id=request.investigation_id,
            collector=self.kind,
            source_type=SourceType.WEB_PAGE,
            url=str(response.url),
            content=content,
            metadata={
                "http_status": response.status_code,
                "content_type": content_type,
                "content_length": len(content),
                "headers": dict(response.headers),
            },
        )
        return [result]
