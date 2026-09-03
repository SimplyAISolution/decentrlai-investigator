from .models import SearchHit

class FakeSearchProvider:
    async def search(self, query: str, limit: int) -> list[SearchHit]:
        results = [
            SearchHit(
                title="Example Domain",
                url="https://example.com",
                snippet=f"Fake result for query: {query}",
                rank=1,
            )
        ]
        return results[:limit]
