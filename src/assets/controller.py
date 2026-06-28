from src.assets.dtos import AssetSchema, AssetEditSchema, AssetBulkSchema, AssetEntity, AssetStatusResponse 
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.assets.model import AssetModel
from fastapi import HTTPException, status
from src.assets.enums import AssetType, AssetStatus
from typing import List, Optional
from datetime import datetime, timezone, date
from fastapi.responses import JSONResponse, Response

from src.relationships import controller
from src.relationships.dtos import RelationshipSchema

from deepmerge import Merger # Merge JSON (metadata)
merger = Merger(
    [(dict, "merge"), (list, "append"), (set, "union")],
    ["override"],  # scalars: override
    ["override"]   # fallback
)

## ------------- Helper -----------------
def create_asset_relationship(from_id: str, to_id: str, db: Session):
    try:
        controller.create_relationship(RelationshipSchema(from_id=from_id, to_id=to_id), db)
    except IntegrityError as e:
        print("Integrity Error while creating relationship:", str(e.orig))

## ------------- Main Function -----------------
def create_asset(body: AssetSchema, response:Response, db: Session):
    data = body.model_dump()

    # 1) Add Lifecycle Status on create
    if data.get("meta").get("expires"):
        exp_date = datetime.strptime(data["meta"]["expires"], "%Y-%m-%d").date()
        if(exp_date >= date.today()):
            data["meta"]["lifecycle_status"] = "expiring soon"
        else :
            data["meta"]["lifecycle_status"] = "expired"

    # Extract Relationships
    covers = data.pop("covers")
    parent = data.pop("parent")

    asset = db.query(AssetModel).get(data["id"])
  
    ## Asset already exists in database
    if asset:
        # reappearing assets will be active/ take the newest status
        asset.status = data["status"]  
        # update source to be the newest
        asset.source = data["source"]
        # merge tags
        old_tags = asset.tags
        new_tags = data.get("tags")
        merged_tags = list(set(old_tags) | set(new_tags))
        asset.tags = merged_tags
        # merge meta data using deepmerge library
        merged_meta = merger.merge(asset.meta, data.get("meta"))
        asset.meta = dict(merged_meta)
        # update last_seen 
        asset.last_seen = datetime.now(timezone.utc)
        print(f"{asset.id}: Asset alreday exists. Updating status, source and last_seen. Merging Tags")
        db.commit()
        db.refresh(asset)
        
        asset_orm = AssetEntity.model_validate(asset, from_attributes=True)
        if response:
            response.status_code=status.HTTP_200_OK
        return AssetStatusResponse (status="Updated", message=f"Asset {asset.id} already exists", asset=asset_orm)
    ## New asset
    else:
        try:
            asset = AssetModel(**data)
            db.add(asset)
            db.commit()
            db.refresh(asset)
            print(f"{asset.id}: New asset created")
            
            asset_orm = AssetEntity.model_validate(asset, from_attributes=True)
            return AssetStatusResponse (status="Created", message=f"Asset {asset.id} created successfully", asset=asset_orm)
        # enforce unique constraints of uq_asset_type_value
        except IntegrityError as e:
            db.rollback()
            print("Integrity Error:", str(e.orig))
            if response: 
                response.status_code=status.HTTP_409_CONFLICT
            return AssetStatusResponse (status="Error", message=f"Duplicate asset {asset.id}: another asset with the same type and value already exists under a different ID.", asset=None)

    
    # Finally create any realationships
    # if covers:
    #     create_asset_relationship(asset.id,covers, db)
    # if parent:
    #     create_asset_relationship(asset.id,parent, db)

    # call create realtionship from relationship controller
    return asset # 201 on create / update (for dedeuplication) - > 201 CREATED

def bulk_create_assets(body: List[AssetBulkSchema], response: Response, db: Session):

    # Get valid assets (don't have missing fields)
    valid_assets = []
    processed_assets = []
    for asset in body:
        
        data = asset.model_dump(exclude_none=True)
        required_fields = ["id", "type", "value", "status", "source"]
        missing = [f for f in required_fields if data.get(f) is None]
        if missing:
            print(f"{asset.id} Invalid asset:\n {data}\n missing: {missing}")
            json_res = {"status": "Error", "message": f"Invalid {asset.id} asset missing: {missing}", "asset": None}
            processed_assets.append(json_res)
            continue
        else:
            valid_assets.append(asset)
            ret = create_asset(asset, None, db)
            processed_assets.append(ret)
        # valid_assets.append(AssetModel(**data))
  
    print(len(valid_assets))
    print(len(body))
    # db.add_all(valid_assets)
    # db.commit()
    
    # for asset in valid_assets:
    #     db.refresh(asset)
    
    # full import failure
    if(len(valid_assets) == 0):
        response.status_code = status.HTTP_400_BAD_REQUEST
    #     raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="All assets were had missing fields")
    
    # Process (create / update / get integrity error) asset one by one
    # for asset in valid_assets:
        # try:
        #     ret = create_asset(asset, None, db)
        #     print("ret---", ret)
        #     processed_assets.append(ret)
        # except HTTPException as e:
        #     print(f"{asset.id}: Integrity error: ", e)

    return  processed_assets # full import / partial import / only updates-> 201 CREATED

def get_assets(db: Session,
    # for filtering
    type: Optional[AssetType],
    status: Optional[AssetStatus],
    tags: Optional[List[str]],
    value: Optional[str],
    # for sorting
    sort: str,
    order: str,
    # for paginataion
    skip: int,
    limit: int ,
    ):
    
    query = db.query(AssetModel)
    # AND  Logic Filtering
    if type:
        query = query.filter(AssetModel.type == type)
    if status:
        query = query.filter(AssetModel.status == status)
    # AND Logic Tagging 
    if tags:
        query = query.filter(AssetModel.tags.contains(tags))
    # Searching by value (LIKE)
    if value:
        print(value)
        query = query.filter(AssetModel.value.ilike(f"%{value}%"))
    
    # Sorting by (id	type	value	status	first_seen	last_seen	source	tags)
    # can not sort by metadata
    try:
        column = getattr(AssetModel, sort)
    except AttributeError:
        column = AssetModel.id
    query = query.order_by(column.desc() if order == "desc" else column.asc())
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    assets = query.all()
    return assets

def get_asset(asset_id: str, db:Session):
    asset = db.query(AssetModel).get(asset_id)

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset ID is not found")
    
    return asset

def update_asset(body: AssetEditSchema, asset_id: str, db:Session):
    asset = db.query(AssetModel).get(asset_id)

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset ID is not found")
    
    body = body.model_dump(exclude_unset=True)
    print(body)
    for key, value in body.items():
        setattr(asset, key, value)

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset

def delete_asset(asset_id: str, db:Session):
    asset = db.query(AssetModel).get(asset_id)

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset ID is not found")
    
    db.delete(asset)
    db.commit()

    return None

