from fastapi import APIRouter, Depends, status, Query, Response
from src.assets import controller
from src.assets.dtos import AssetCreate, AssetEdit, Asset, AssetBulk
from src.utils.db import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from src.utils.dependencies import is_authenticated
from src.auth.model import UserModel
from src.assets.enums import AssetType, AssetStatus
from src.dto_common import ApiResponse, PaginationResponse

assets_routes = APIRouter(prefix="/assets")

# **responses** to document dynmic status codes and responses that don't get documented by default

@assets_routes.post("", response_model= ApiResponse[Asset], status_code=status.HTTP_201_CREATED,
                responses={200: {"description": "Successful Update Response", "model": ApiResponse[Asset]},
                           409: {"description": "Conflict (Duplication) Error", "model": ApiResponse[Asset]},}
                    )
def create_asset(body: AssetCreate, response: Response, db: Session = Depends(get_db), 
                 user:UserModel = Depends(is_authenticated)):
    return controller.create_asset(body, response, db)


@assets_routes.post("/bulk-create", response_model=List[ApiResponse[Asset]], status_code=status.HTTP_200_OK,
                        responses={400: {"description": "All Bulk Failed", "model": List[ApiResponse[Asset]]}}
                    )
def bulk_create_assets(body: List[AssetBulk], response: Response, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.bulk_create_assets(body, response, db)


@assets_routes.get("", response_model=PaginationResponse[Asset], status_code=status.HTTP_200_OK)
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
    limit: int = 50,
    ):
    return controller.get_assets(db, 
            type, status, tags, value, 
            sort, order,
            skip, limit)


@assets_routes.get("/{asset_id}", response_model=ApiResponse[Asset],status_code=status.HTTP_200_OK,
                    responses={404: {"description": "Not Found Error", "model": ApiResponse[Asset]}}
                   )
def get_asset(asset_id: str, response: Response, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.get_asset(asset_id, response, db)



@assets_routes.patch("/{asset_id}", response_model=ApiResponse[Asset], status_code=status.HTTP_200_OK,
                        responses={404: {"description": "Not Found Error", "model": ApiResponse[Asset]}}
                     )
def update_asset(body: AssetEdit, asset_id: str, response:Response, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.update_asset(body, asset_id, response, db)


@assets_routes.delete("/{asset_id}", response_model= None, status_code=status.HTTP_204_NO_CONTENT,
                        responses={404: {"description": "Not Found Error"}}
                      )
def delete_task(asset_id: str, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.delete_asset(asset_id, db)

