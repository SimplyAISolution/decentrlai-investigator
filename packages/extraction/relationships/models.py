from pydantic import BaseModel, Field

class Relationship(BaseModel):
    source_entity: str = Field(description="The exact name of the subject/source entity.")
    target_entity: str = Field(description="The exact name of the object/target entity.")
    relationship_type: str = Field(
        description="The type of relationship (e.g., FOUNDER_OF, EMPLOYED_BY, LOCATED_IN, ACQUIRED, PARTNERED_WITH). Always use UPPERCASE."
    )
    context: str = Field(description="A brief explanation of how these entities are related based on the text.")

class ExtractedRelationships(BaseModel):
    relationships: list[Relationship] = Field(
        default_factory=list, 
        description="A list of all discovered relationships between entities."
    )
