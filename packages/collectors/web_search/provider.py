from __future__ import annotations
from typing import Protocol
from .models import SearchHit

class SearchProvider(Protocol):
    async def search(self, query: str, limit: int) -> list[SearchHit]:
        ...
