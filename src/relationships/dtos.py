from pydantic import BaseModel
from src.relationships.enums import RelationshipsType
from src.assets.dtos import AssetEntity

class RelationshipSchema(BaseModel):
    from_id: str
    to_id: str

# class RelationshipEditSchema(BaseModel):
#     from_id: str | None = None
#     to_id: str | None = None

class Relationship(BaseModel):
    id: int
    from_id: str
    to_id: str
    type: RelationshipsType 

class RelationshipResponseSchema(BaseModel):
    id: int
    from_id: str
    to_id: str
    type: RelationshipsType 
    from_asset: AssetEntity 
    to_asset: AssetEntity 

class RelationshipStatusResponse(BaseModel):
    status: str
    message: str
    id: int | None = None
    from_asset: AssetEntity | None = None
    to_asset: AssetEntity | None = None
    type: RelationshipsType | None = None
 

class AssetRelationship(BaseModel):
    id: str
    parent: str | None = None
    covers: str | None = None


class AssetRelationshipBulk(BaseModel):
    id: str | None = None
    parent: str | None = None
    covers: str | None = None


