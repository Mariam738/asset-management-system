from fastapi import APIRouter, Depends, status, Query, Response
from src.assets import controller
from src.assets.dtos import AssetSchema, AssetEditSchema, AssetResponseSchema, AssetBulkSchema, AssetStatusResponse 
from src.utils.db import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from src.utils.helpers import is_authenticated
from src.auth.model import UserModel
from src.assets.enums import AssetType, AssetStatus

assets_routes = APIRouter(prefix="/assets")

# **responses** to document dynmic status codes and responses that don't get documented by default

@assets_routes.post("", response_model=AssetStatusResponse , status_code=status.HTTP_201_CREATED,
                responses={200: {"description": "Successful Update Response", "model": AssetStatusResponse},
                           409: {"description": "Conflict (Duplication) Error", "model": AssetStatusResponse},}
                    )
def create_asset(body: AssetSchema, response: Response, db: Session = Depends(get_db), 
                 user:UserModel = Depends(is_authenticated)):
    return controller.create_asset(body, response, db)


@assets_routes.post("/bulk", response_model=List[AssetStatusResponse ], status_code=status.HTTP_200_OK,
                        responses={400: {"description": "All Bulk Failed", "model": AssetStatusResponse}}
                    )
def bulk_create_assets(body: List[AssetBulkSchema], response: Response, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.bulk_create_assets(body, response, db)


@assets_routes.get("", response_model=List[AssetResponseSchema], status_code=status.HTTP_200_OK)
def get_assets(db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated),
    # for filtering
    type: Optional[AssetType] = Query(None),
    status: Optional[AssetStatus] =  Query(None),
    tags: Optional[List[str]] = Query(None),
    value: Optional[str] = Query(None),
    # for sorting
    sort: str = "id",
    order: str ="asc",
    # for paginataion
    skip: int = 0,
    limit: int = 25,
    ):
    return controller.get_assets(db, 
            type, status, tags, value, 
            sort, order,
            skip, limit)


@assets_routes.get("/{asset_id}", response_model=AssetResponseSchema, status_code=status.HTTP_200_OK,
                    responses={404: {"description": "Not Found Error"}}
                   )
def get_asset(asset_id: str, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.get_asset(asset_id, db)



@assets_routes.patch("/{asset_id}", response_model=AssetResponseSchema, status_code=status.HTTP_200_OK,
                        responses={404: {"description": "Not Found Error"}}
                     )
def update_asset(body: AssetEditSchema, asset_id: str, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.update_asset(body, asset_id, db)



@assets_routes.delete("/{asset_id}", response_model= None, status_code=status.HTTP_204_NO_CONTENT,
                        responses={404: {"description": "Not Found Error"}}
                      )
def delete_task(asset_id: str, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.delete_asset(asset_id, db)

