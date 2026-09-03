from pydantic import BaseModel, Field

class Entity(BaseModel):
    name: str = Field(description="The normalized name of the entity.")
    type: str = Field(description="Strictly one of: PERSON, ORGANIZATION, LOCATION, PRODUCT, or OTHER.")
    context: str = Field(description="A brief, 1-sentence description of how this entity is mentioned in the text.")

class ExtractedEntities(BaseModel):
    entities: list[Entity] = Field(default_factory=list, description="A list of all discovered entities.")
