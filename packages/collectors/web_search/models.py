from dataclasses import dataclass

@dataclass(slots=True)
class SearchHit:
    title: str
    url: str
    snippet: str | None = None
    rank: int | None = None
