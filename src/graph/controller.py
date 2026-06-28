from src.assets.dtos import Asset
from src.graph.dtos import GraphNode
from src.relationships.models import RelationshipModel
from sqlalchemy.orm import Session
from src.assets.model import AssetModel
from fastapi import HTTPException, status


def get_children(asset_id: str, db: Session):
    children = db.query(RelationshipModel).filter(RelationshipModel.to_id == asset_id).all()

    asset = db.query(AssetModel).filter(AssetModel.id == asset_id).first()
    asset = Asset.model_validate(asset, from_attributes=True)
    node = GraphNode(asset=asset, children=[])

    for child in children:
        child_node = get_children(child.from_id, db)
        node.children.append(child_node)

    return node

def get_root_id(asset_id: str, db: Session):
    parents = db.query(RelationshipModel).filter(RelationshipModel.from_id == asset_id).all()

    if not parents:
        return asset_id
    
    # ASSUMING there is always a
    # Then ofcouse domain will always be at top
    parent = parents[0]
    return get_root_id(parent.to_id, db)

def get_graph(asset_id: str, db: Session):
    asset = db.query(AssetModel).get(asset_id)

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset ID is not found")
    
    root_id =  get_root_id(asset_id, db)
    return get_children(root_id, db)