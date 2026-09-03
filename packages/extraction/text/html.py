from bs4 import BeautifulSoup
import trafilatura

from packages.evidence.models.evidence import Evidence
from packages.extraction.text.models import ExtractedDocument, compute_text_hash

class HTMLExtractor:
    def extract(self, evidence: Evidence, raw_content: bytes) -> ExtractedDocument:
        # 1. Isolate the core readable text
        extracted_text = trafilatura.extract(
            raw_content,
            include_links=True,
            include_formatting=True,
            no_fallback=False
        ) or ""

        # 2. Extract structured metadata
        soup = BeautifulSoup(raw_content, "html.parser")
        
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        
        meta_tags = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                # Standardize keys to lowercase for easier querying
                meta_tags[name.lower()] = content.strip()

        # Fallback to OpenGraph title if standard title is missing
        if not title and "og:title" in meta_tags:
            title = meta_tags["og:title"]

        text_hash = compute_text_hash(extracted_text)

        return ExtractedDocument(
            evidence_id=evidence.evidence_id,
            investigation_id=evidence.investigation_id,
            title=title,
            clean_text=extracted_text,
            text_hash=text_hash,
            metadata=meta_tags,
        )
