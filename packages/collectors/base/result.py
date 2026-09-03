from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from .types import CollectorKind, SourceType

@dataclass(slots=True)
class CollectionResult:
    investigation_id: UUID
    collector: CollectorKind
    source_type: SourceType
    url: str | None = None
    title: str | None = None
    content: str | bytes | None = None
    result_id: UUID = field(default_factory=uuid4)
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_result_id: UUID | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "result_id": str(self.result_id),
            "investigation_id": str(self.investigation_id),
            "collector": self.collector.value,
            "source_type": self.source_type.value,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "retrieved_at": self.retrieved_at.isoformat(),
            "metadata": self.metadata,
            "parent_result_id": str(self.parent_result_id) if self.parent_result_id else None,
        }
