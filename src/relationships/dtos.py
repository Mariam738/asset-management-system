from pydantic import BaseModel
from src.relationships.enums import RelationshipsType
from src.assets.dtos import Asset
from typing import List

class Relationship(BaseModel):
    id: int 
    from_asset: Asset 
    to_asset: Asset 
    type: RelationshipsType 

# Minimal return till ids on create and bulk create
class RelationshipResponse(BaseModel):
    status: str
    message: str
    data: Relationship | None = None


class RelationshipCreate(BaseModel):
    id: str
    parent: str | None = None
    covers: str | None = None

# All nulls -> so missing data don't make failures in bulk
class RelationshipBulk(BaseModel):
    id: str | None = None
    parent: str | None = None
    covers: str | None = None

class RelationshipPaginationResponse(BaseModel):
    total: int
    skip: int
    limit: int
    count: int
    data: List[Relationship]


