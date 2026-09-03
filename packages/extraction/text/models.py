from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
import hashlib

def compute_text_hash(text: str) -> str:
    """Creates a semantic fingerprint for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

@dataclass(slots=True)
class ExtractedDocument:
    evidence_id: UUID
    investigation_id: UUID
    
    title: str | None
    clean_text: str
    text_hash: str
    
    metadata: dict[str, str] = field(default_factory=dict)
    
    extraction_id: UUID = field(default_factory=uuid4)
    extracted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def as_dict(self) -> dict:
        return {
            "extraction_id": str(self.extraction_id),
            "evidence_id": str(self.evidence_id),
            "investigation_id": str(self.investigation_id),
            "title": self.title,
            "text_hash": self.text_hash,
            "text_length": len(self.clean_text),
            "metadata": self.metadata,
        }
