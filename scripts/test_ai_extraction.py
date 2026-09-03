import asyncio
from packages.extraction.entities.extractor import AIEntityExtractor

async def main() -> None:
    # We use a controlled text to guarantee entities exist for the test
    mock_investigation_text = """
    On August 14, 2026, Jane Doe, the CEO of Acme Robotics, announced a major 
    expansion of their manufacturing facilities in Detroit, Michigan. The project, 
    funded by a $50M grant from Global Tech Ventures, will focus on producing 
    the new Sentinel-X autonomous drone systems. Operations are expected to be 
    overseen by Chief Engineer Marcus Vance.
    """

    print("\n=== STARTING LOCAL AI ENTITY EXTRACTION ===")
    print("Connecting to local Ollama instance (ensure model 'llama3.1' is pulled)...")
    
    # Initialize the extractor (defaults to llama3.1)
    extractor = AIEntityExtractor(model_name="llama3.1")
    
    print("\nAnalyzing text...")
    result = await extractor.extract(mock_investigation_text)

    print(f"\n=== EXTRACTION RESULTS ({len(result.entities)} found) ===")
    for entity in result.entities:
        print(f"[{entity.type}] {entity.name}")
        print(f"    -> {entity.context}\n")

if __name__ == "__main__":
    asyncio.run(main())
