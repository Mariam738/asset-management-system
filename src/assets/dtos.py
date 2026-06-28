from pydantic import BaseModel, Field
from src.assets.enums import AssetType, AssetStatus
from datetime import datetime
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

# No Nulls, Allow Defaults -> Strong INPUT VALIDATION
class AssetCreate(BaseModel):
    id: str 
    type: AssetType 
    value: str 
    status: AssetStatus 

    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    source: str 
    tags: List[str]  = Field(default_factory=list)
    meta: Dict[str, Any]  = Field(default_factory=dict, alias="metadata") # alis is the solution to metadata being reserved in sqlalchemy


# Allow Null, Allow Defaults -> Bulk is usually unclean, with duplicates
class AssetBulk(BaseModel):
    id: str | None = None
    type: AssetType | None = None
    value: str | None = None
    status: AssetStatus | None = None

    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    source: str | None = None
    tags: List[str]  = Field(default_factory=list)
    meta: Dict[str, Any]  = Field(default_factory=dict, alias="metadata") # alis is the solution to metadata being reserved in sqlalchemy

    
# All Optional -> Support PUT
class AssetEdit(BaseModel):
    id: str | None = None
    type: AssetType | None = None
    value: str | None = None
    status: AssetStatus | None = None

    first_seen: datetime | None = None
    last_seen : datetime | None = None

    source: str | None = None
    tags: List[str]  | None = None
    meta: Dict[str, Any]  | None = Field(None, alias="metadata") # alis is the solution to metadata being reserved in sqlalchemy

# -> Return data from db
class Asset(BaseModel):
    id: str 
    type: AssetType 
    value: str 
    status: AssetStatus 

    first_seen: datetime 
    last_seen : datetime 

    source: str 
    tags: List[str] 
    meta: Dict[str, Any]  




    