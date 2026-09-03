from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

@dataclass(slots=True)
class CollectionRequest:
    investigation_id: UUID
    query: str | None = None
    url: str | None = None
    max_results: int = 10
    timeout_seconds: float = 20.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.query and not self.url:
            raise ValueError("CollectionRequest requires at least one of query or url.")
        if self.max_results <= 0:
            raise ValueError("max_results must be greater than zero.")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero.")
