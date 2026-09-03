from __future__ import annotations
import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from .models import ExtractedEntities

logger = logging.getLogger(__name__)

class AIEntityExtractor:
    def __init__(self, model_name: str = "llama3.1"):
        # Initialize local LLM with zero temperature for factual consistency
        self.llm = ChatOllama(model=model_name, temperature=0.0)
        
        # Bind the Pydantic schema to enforce JSON output
        self.structured_llm = self.llm.with_structured_output(ExtractedEntities)

        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an expert OSINT analyst. Your objective is to extract all named entities "
                "(People, Organizations, Locations, Products) from the provided text. "
                "Do not hallucinate. If no entities exist, return an empty list."
            ),
            ("human", "TEXT TO ANALYZE:\n{text}")
        ])

        self.chain = self.prompt | self.structured_llm

    async def extract(self, text: str) -> ExtractedEntities:
        if not text.strip():
            return ExtractedEntities(entities=[])

        # Truncate text to roughly 6,000 characters to prevent context window overflow
        # during this initial phase (prior to implementing text chunking)
        safe_text = text[:6000]
        
        try:
            return await self.chain.ainvoke({"text": safe_text})
        except Exception as exc:
            logger.error(f"Entity extraction failed: {exc}")
            # Fallback to empty list on failure
            return ExtractedEntities(entities=[])
