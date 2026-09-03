from __future__ import annotations
import logging
from duckduckgo_search import AsyncDDGS

from packages.collectors.web_search.models import SearchHit
from packages.collectors.web_search.provider import SearchProvider

logger = logging.getLogger(__name__)

class DuckDuckGoSearchProvider(SearchProvider):
    async def search(self, query: str, limit: int) -> list[SearchHit]:
        hits: list[SearchHit] = []
        try:
            # AsyncDDGS natively fetches keyless search results from DuckDuckGo
            results = await AsyncDDGS().text(query, max_results=limit)
            
            if not results:
                return hits
                
            for idx, r in enumerate(results, start=1):
                hits.append(
                    SearchHit(
                        title=r.get("title", "No Title"),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        rank=idx
                    )
                )
        except Exception as exc:
            logger.error(f"DuckDuckGo search failed: {exc}")
            
        return hits
