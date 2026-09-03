from __future__ import annotations
import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from .models import ExtractedRelationships

logger = logging.getLogger(__name__)

class AIRelationshipExtractor:
    def __init__(self, model_name: str = "llama3.1"):
        self.llm = ChatOllama(model=model_name, temperature=0.0)
        self.structured_llm = self.llm.with_structured_output(ExtractedRelationships)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert OSINT analyst building a knowledge graph. "
                "Extract all relationships between named entities in the provided text. "
                "Return a list mapping a source entity to a target entity with a distinct relationship type. "
                "If no relationships exist, return an empty list."
            ),
            ("human", "TEXT TO ANALYZE:\n{text}")
        ])

        self.chain = self.prompt | self.structured_llm

    async def extract(self, text: str) -> ExtractedRelationships:
        if not text.strip():
            return ExtractedRelationships(relationships=[])

        safe_text = text[:6000]
        
        try:
            return await self.chain.ainvoke({"text": safe_text})
        except Exception as exc:
            logger.error(f"Relationship extraction failed: {exc}")
            return ExtractedRelationships(relationships=[])
