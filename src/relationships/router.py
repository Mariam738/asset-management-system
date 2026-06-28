from fastapi import APIRouter, Depends, status, Query, Response
from src.relationships import controller
from src.relationships.dtos import RelationshipSchema, RelationshipResponseSchema, AssetRelationship, RelationshipStatusResponse, AssetRelationshipBulk
from src.relationships.enums import RelationshipsType
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.utils.helpers import is_authenticated
from src.auth.model import UserModel
from typing import List, Optional

relationships_routes = APIRouter(prefix="/relationships")

@relationships_routes.post("", response_model=RelationshipStatusResponse, status_code=status.HTTP_201_CREATED,
                           responses={400: {"description": "Invalid Relationship Error", "model": RelationshipStatusResponse},
                                     404: {"description": "Not Found Error", "model": RelationshipStatusResponse},
                                     409: {"description": "Conflict (Duplication) Error", "model": RelationshipStatusResponse},
                                     }
                           )
def create_relationship(body: AssetRelationship, response:Response, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.create_relationship(body, response, db)


@relationships_routes.post("/bulk", response_model=List[RelationshipStatusResponse], status_code=status.HTTP_200_OK,
                                responses={400: {"description": "All Bulk Failed", "model": RelationshipStatusResponse},}
                           )
def bulk_create_relationship(body: List[AssetRelationshipBulk], response:Response, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.bulk_create_relationship(body, response, db)


@relationships_routes.get("", response_model=List[RelationshipResponseSchema],status_code=status.HTTP_200_OK)
def get_relationships(db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated),
    # for filtering
    type: Optional[RelationshipsType] = Query(None),
    from_id: Optional[str] =  Query(None),
    to_id: Optional[str] = Query(None),
    # for sorting
    sort: str = "id",
    order: str ="asc",
    # for paginataion
    skip: int = 0,
    limit: int = 25,
    ):
        return controller.get_relationships(db,
            type, from_id, to_id,
            sort, order,
            skip, limit)


@relationships_routes.get("/{relationship_id}", response_model=RelationshipResponseSchema, status_code=status.HTTP_200_OK,
                        responses={404: {"description": "Not Found Error"}}
                        )
def get_relationshiip(relationship_id: int, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.get_relationship(relationship_id, db)


@relationships_routes.put("/{relationship_id}", response_model=RelationshipStatusResponse, status_code=status.HTTP_200_OK,
                        responses={400: {"description": "Invalid Relationship Error", "model": RelationshipStatusResponse},
                                     404: {"description": "Not Found Error", "model": RelationshipStatusResponse},
                                     409: {"description": "Conflict (Duplication) Error", "model": RelationshipStatusResponse},}
                          )
def edit_relationship(body: AssetRelationship, response: Response ,relationship_id: int, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.edit_relationship(body, response, relationship_id, db)



@relationships_routes.delete("/{relationship_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT,
                                responses={404: {"description": "Not Found Error"}}
                             )
def delete_relationship(relationship_id: int, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
    return controller.delete_relationship(relationship_id, db)

