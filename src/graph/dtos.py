from src.assets.enums import AssetType, AssetStatus
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

class GraphNode(BaseModel):
    # AssetResponseSchmet
    id: str 
    type: AssetType 
    value: str 
    status: AssetStatus 

    first_seen: datetime 
    last_seen : datetime 

    source: str 
    tags: List[str] 
    meta: Dict[str, Any]  

    children: List["GraphNode"] = Field(default_factory=list)


GraphNode.model_rebuild()