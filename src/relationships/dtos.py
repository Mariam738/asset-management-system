from pydantic import BaseModel
from src.relationships.enums import RelationshipsType
from src.assets.dtos import Asset
from typing import List

class Relationship(BaseModel):
    id: int 
    from_asset: Asset 
    to_asset: Asset 
    type: RelationshipsType 

class RelationshipCreate(BaseModel):
    id: str
    parent: str | None = None
    covers: str | None = None

# All nulls -> so missing data don't make failures in bulk
class RelationshipBulk(BaseModel):
    id: str | None = None
    parent: str | None = None
    covers: str | None = None



