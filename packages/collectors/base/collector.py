from __future__ import annotations
from abc import ABC, abstractmethod
from .request import CollectionRequest
from .result import CollectionResult
from .types import CollectorKind

class Collector(ABC):
    kind: CollectorKind

    async def execute(self, request: CollectionRequest) -> list[CollectionResult]:
        request.validate()
        await self.validate_request(request)
        results = await self.collect(request)
        normalized_results: list[CollectionResult] = []
        for result in results:
            normalized = await self.normalize(result)
            if normalized is not None:
                normalized_results.append(normalized)
        return normalized_results

    async def validate_request(self, request: CollectionRequest) -> None:
        return None

    @abstractmethod
    async def collect(self, request: CollectionRequest) -> list[CollectionResult]:
        raise NotImplementedError

    async def normalize(self, result: CollectionResult) -> CollectionResult | None:
        return result
