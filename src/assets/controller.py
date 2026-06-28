from src.assets.dtos import AssetCreate, AssetEdit, AssetBulk, Asset, AssetResponse, AssetPaginationResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.assets.model import AssetModel
from fastapi import HTTPException, status
from src.assets.enums import AssetType, AssetStatus
from typing import List, Optional
from datetime import datetime, timezone, date
from fastapi.responses import Response


from deepmerge import Merger # Merge JSON (metadata)
merger = Merger(
    [(dict, "merge"), (list, "append"), (set, "union")],
    ["override"],  # scalars: override
    ["override"]   # fallback
)


## ------------- Main Function -----------------
def create_asset(body: AssetCreate, response:Response, db: Session):
    data = body.model_dump()

    # 1) Add Lifecycle Status on create
    if data.get("meta").get("expires"):
        exp_date = datetime.strptime(data["meta"]["expires"], "%Y-%m-%d").date()
        if(exp_date >= date.today()):
            data["meta"]["lifecycle_status"] = "expiring soon"
        else :
            data["meta"]["lifecycle_status"] = "expired"

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
        
        asset_orm = Asset.model_validate(asset, from_attributes=True)
        if response:
            response.status_code=status.HTTP_200_OK
        return AssetResponse (status="Updated", message=f"Asset {asset.id} already exists", asset=asset_orm)
    ## New asset
    else:
        try:
            print("------data",data)
            asset = AssetModel(**data)
            db.add(asset)
            db.commit()
            db.refresh(asset)
            
            asset_orm = Asset.model_validate(asset, from_attributes=True)
            return AssetResponse (status="Created", message=f"Asset {asset.id} created successfully", asset=asset_orm)
        # enforce unique constraints of uq_asset_type_value
        except IntegrityError as e:
            db.rollback()
            print("Integrity Error:", str(e.orig))
            if response: 
                response.status_code=status.HTTP_409_CONFLICT
            return AssetResponse (status="Error", message=f"Duplicate asset {asset.id}: another asset with the same type and value already exists under a different ID.", asset=None)


def bulk_create_assets(body: List[AssetBulk], response: Response, db: Session):

    # Get valid assets (don't have missing fields)
    valid_cnt = 0
    processed_assets = []
    for asset in body:
        
        data = asset.model_dump(exclude_none=True)
        required_fields = ["id", "type", "value", "status", "source"]
        missing = [f for f in required_fields if data.get(f) is None]
        if missing:
            json_res = {"status": "Error", "message": f"Invalid {asset.id} asset missing: {missing}", "asset": None}
            processed_assets.append(json_res)
            continue
        else:
            # Process valid assets
            valid_cnt += 1
            ret = create_asset(asset, None, db)
            processed_assets.append(ret)

    # full import failure
    if(valid_cnt == 0):
        response.status_code = status.HTTP_400_BAD_REQUEST
    
    return  processed_assets 


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
    total = query.count()
    query = query.offset(skip).limit(limit)
    
    assets = query.all()
    data= [Asset.model_validate(asset, from_attributes=True) for asset in assets]
    
    return AssetPaginationResponse(total=total, skip=skip, limit=limit, count=len(data), data= data)


def get_asset(asset_id: str, response: Response, db:Session):
    asset = db.query(AssetModel).get(asset_id)

    if not asset:
        response.status_code = status.HTTP_404_NOT_FOUND
        return AssetResponse(status="Error", message="Asset ID is not found", asset= None)
    
    asset = Asset.model_validate(asset, from_attributes=True)
    return AssetResponse(status="Success", message="Asset retrieved successfully", asset= asset)


def update_asset(body: AssetEdit, asset_id: str, response: Response, db:Session):
    asset = db.query(AssetModel).get(asset_id)

    if not asset:
        response.status_code = status.HTTP_404_NOT_FOUND
        return AssetResponse(status="Error", message="Asset ID is not found", asset= None)
    
    body = body.model_dump(exclude_unset=True)
    for key, value in body.items():
        setattr(asset, key, value)

    db.add(asset)
    db.commit()
    db.refresh(asset)

    asset = Asset.model_validate(asset, from_attributes=True)
    return AssetResponse(status="Updated", message="Asset updated successfully", asset= asset)


def delete_asset(asset_id: str, db:Session):
    asset = db.query(AssetModel).get(asset_id)

    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset ID is not found")
    
    db.delete(asset)
    db.commit()

    return None

