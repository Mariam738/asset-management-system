from sqlalchemy.orm import Session
from src.relationships.dtos import Relationship, RelationshipSchema, AssetRelationship, RelationshipStatusResponse, AssetRelationshipBulk, RelationshipResponseSchema
from src.assets.model import AssetModel
from fastapi import HTTPException, status, Query
from src.relationships.enums import RelationshipsType
from src.assets.enums import AssetType
from src.relationships.models import RelationshipModel
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from fastapi import Response
from src.assets.dtos import AssetEntity

## ------ Helpers ------
def infer_relationship_type(from_type, to_type):

    if from_type == AssetType.SUBDOMAIN and to_type == AssetType.DOMAIN:
        return RelationshipsType.SUBDOMAIN_TO_DOMAIN
    
    elif from_type == AssetType.SERVICE and to_type == AssetType.IP_ADDRESS:
        return RelationshipsType.SERVICE_TO_IP
    
    # avoid duplicate entries in <--> bidirectional realationship
    elif from_type == AssetType.IP_ADDRESS and to_type == AssetType.SUBDOMAIN:
        return RelationshipsType.IP_TO_SUBDOMAIN
    elif from_type == AssetType.SUBDOMAIN and to_type == AssetType.IP_ADDRESS:
        return -1
    
    elif from_type == AssetType.CERTIFICATE and to_type == AssetType.DOMAIN:
        return RelationshipsType.CERTIFICATE_TO_DOMAIN
    elif from_type == AssetType.CERTIFICATE and to_type == AssetType.SUBDOMAIN:
        return RelationshipsType.CERTIFICATE_TO_SUBDOMAIN
    
    elif from_type == AssetType.TECHNOLOGY and to_type == AssetType.SUBDOMAIN:
        return RelationshipsType.TECHNOLOGY_TO_SUBDOMAIN
    
    elif from_type == AssetType.TECHNOLOGY and to_type == AssetType.SERVICE:
        return RelationshipsType.TECHNOLOGY_TO_SERVICE

    return None

def expand_relationship(relationship: RelationshipModel, db: Session):
    relationship = Relationship.model_validate(relationship, from_attributes=True)
    from_asset = db.query(AssetModel).get(relationship.from_id)
    to_asset = db.query(AssetModel).get(relationship.to_id)
    
    response = RelationshipResponseSchema(
        **relationship.model_dump(),
        from_asset=AssetEntity.model_validate(from_asset, from_attributes=True),
        to_asset=AssetEntity.model_validate(to_asset, from_attributes=True)
    )
    return response

def validate_input_relationship(data, response: Response, db: Session):

    parent = data.get("parent") 
    covers = data.get("covers") 
    if not parent and not covers:
        if response:
            response.status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        return RelationshipStatusResponse(status="Error", message="Invalid relationship: missing fields 'parent' or 'covers'", id=None,
                                          from_asset=None, to_asset= None, type= None)
    if parent and covers:
        if response:
            response.status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
        return RelationshipStatusResponse(status="Error", message="Invalid relationship: one field is required either'parent' or 'covers'", id=None,
                                          from_asset=None, to_asset= None, type= None)
    return True

def validate_from_asset(data, response: Response, db: Session):
    id = data["id"]
    print("idddddd", id)
    from_asset = db.query(AssetModel).get(id)
    print(from_asset)
    if not from_asset:
        if response:
            response.status_code = status.HTTP_404_NOT_FOUND
        return RelationshipStatusResponse(status="Error", message="Invalid relationship: From asset ID is not found'",
                                          id=None,from_asset=None, to_asset= None, type= None)
    data["from_id"] = data.pop("id")
    return from_asset

def validate_to_asset(data, response: Response, db: Session):
    parent = data.get("parent") 
    covers = data.get("covers") 

    if parent:
        to_id = parent
        data["to_id"] = data.pop("parent")
        data.pop("covers")
    else:
        to_id = covers
        data["to_id"] = data.pop("covers")
        data.pop("parent")

    to_asset = db.query(AssetModel).get(to_id)
    if not to_asset:
        if response:
            response.status_code = status.HTTP_404_NOT_FOUND
        return RelationshipStatusResponse(status="Error", message="Invalid relationship: To asset ID is not found'",
                                          id=None,from_asset=None, to_asset= None, type= None)
    return to_asset


# Helper used in create and edit
def save_relationship_helper(body: AssetRelationship, response: Response, db: Session):
    data = body.model_dump()

    # 1) validate input data
    result = validate_input_relationship(data, response, db)
    if isinstance(result, RelationshipStatusResponse):
        return result

    # 2) validate from asset
    from_asset = validate_from_asset(data, response, db)
    print(from_asset)
    if isinstance(from_asset, RelationshipStatusResponse):
        return from_asset

    # 3) validate to asset
    to_asset = validate_to_asset(data, response, db)
    if isinstance(to_asset, RelationshipStatusResponse):
        return to_asset
        
    print(from_asset.type)
    print(to_asset.type)
    print(data)

    # 4) validate relationship
    inferred_type = infer_relationship_type(from_asset.type, to_asset.type)

    if inferred_type is None:
        if response:
            response.status_code = status.HTTP_400_BAD_REQUEST
        return RelationshipStatusResponse(status="Error", message=f"Invalid relationship type between assets: {from_asset.type.value} -> {to_asset.type.value}'",
                                    id=None,from_asset=None, to_asset= None, type= None)
    
    # Ensure 1 record IP->SUBDMAIN (No duplicated reversed rows) 
    if inferred_type == -1:    
        data["from_id"] = to_asset.id
        data["to_id"] = from_asset.id
        inferred_type = RelationshipsType.IP_TO_SUBDOMAIN

    data["type"] = inferred_type

    # 5) Return data
    return data, from_asset, to_asset
  

## ------ Functions ------

def create_relationship(body: AssetRelationship, response: Response, db: Session):
    
    result = save_relationship_helper(body, response, db)
    if isinstance(result, RelationshipStatusResponse):
        return result
    
    data, from_asset, to_asset = result

    relationship = RelationshipModel(**data)
    from_asset = AssetEntity.model_validate(from_asset, from_attributes=True)
    to_asset = AssetEntity.model_validate(to_asset, from_attributes=True)
    try:
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        return RelationshipStatusResponse(status="Created", message=f"Relationship {relationship.id} created successfully",
                                    id=relationship.id,from_asset=from_asset, to_asset= to_asset, type= data["type"])
    # enforce unique constraints of uq_relationship_from_to
    except IntegrityError as e:
        db.rollback()
        print("Integrity Error:", str(e.orig))
        if response:
            response.status_code = status.HTTP_409_CONFLICT
        return RelationshipStatusResponse(status="Error", message="Duplicate relationship: another relationship with the same from_id and to_id already exists under a different ID.",
                                    id=None,from_asset=None, to_asset= None, type= None)


def bulk_create_relationship(body: List[AssetRelationshipBulk], response: Response, db: Session):
    
    valid = []
    processed = []

    for relationship in body:
        data = relationship.model_dump(exclude_none=True)
        if not data.get("id"):
            json_res = {"status": "Error", "message": f"Invalid relationship missing: is", "id":None,
                                          "from_asset":None, "to_asset": None, "type": None}
            processed.append(json_res)
        else:
            valid.append(relationship)
            ret = create_relationship(relationship, None, db)
            print("ret------")
            processed.append(ret)

    if(len(valid) == 0):
        response.status_code = status.HTTP_400_BAD_REQUEST

    return processed

def get_relationships(db: Session,
    # for filtering
    type: Optional[RelationshipsType],
    from_id: Optional[str],
    to_id: Optional[str],
    # for sorting
    sort: str,
    order: str,
    # for paginataion
    skip: int,
    limit: int 
    ):
    query = db.query(RelationshipModel)
    # AND FILTERING
    if type:
        query = query.filter(RelationshipModel.type == type)
    if from_id:
        query = query.filter(RelationshipModel.from_id == from_id)
    if to_id:
        query = query.filter(RelationshipModel.to_id == to_id)

    # Sorting
    print(skip)
    try:
        column = getattr(RelationshipModel, sort)
    except AttributeError:
        column = RelationshipModel.id
    query = query.order_by(column.desc() if order == "desc" else column.asc())

    # Pagination
    query = query.offset(skip).limit(limit)

    relations = query.all()

    response = []
    for relation in relations:
        response.append(expand_relationship(relation, db))
    return response

def get_relationship(relationship_id: int, db: Session):
    relationship = db.query(RelationshipModel).get(relationship_id)

    if not relationship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship ID is not found")
    
    return expand_relationship(relationship, db)
    
    
  

def edit_relationship(body: RelationshipSchema,response: Response, relationship_id: int, db: Session):
    relationship = db.query(RelationshipModel).get(relationship_id)
    if not relationship:
        response.status_code = status.HTTP_404_NOT_FOUND
        return RelationshipStatusResponse(status="Error", message="Relationship ID is not found.",
                                    id=None,from_asset=None, to_asset= None, type= None)
    
    result = save_relationship_helper(body, response, db)
    if isinstance(result, RelationshipStatusResponse):
        return result
    
    data, from_asset, to_asset = result
    
  
    for key, value in data.items():
        setattr(relationship, key, value)
      

    try:
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        from_asset = AssetEntity.model_validate(from_asset, from_attributes=True)
        to_asset = AssetEntity.model_validate(to_asset, from_attributes=True)
        
        # relationship = Relationship.model_validate(relationship, from_attributes=True)

        return RelationshipStatusResponse(status="Updated", message=f"Relationship {relationship.id} created successfully",
                                    id=relationship.id,from_asset=from_asset, to_asset= to_asset, type= data["type"])
    

    # enforce unique constraints of uq_relationship_from_to
    except IntegrityError as e:
        db.rollback()
        print("Integrity Error:", str(e.orig))
        response.status_code = status.HTTP_409_CONFLICT
        return RelationshipStatusResponse(status="Error", message="Duplicate relationship: another relationship with the same from_id and to_id already exists under a different ID.",
                                    id=None,from_asset=None, to_asset= None, type= None)
    

    # if data.get("from_id"):
    #     from_asset = db.query(AssetModel).get(data["from_id"])
    #     if not from_asset:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="From asset ID is not found")
    #     else: 
    #         from_type = from_asset.type
    # else:
    #     from_type = str(relationship.type).lower().split("_")[0]
    
    # if data.get("to_id"):
    #     to_asset = db.query(AssetModel).get(data["to_id"])
    #     if not to_asset:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="To asset ID is not found")
    #     else: 
    #         to_type = to_asset.type
    # else:
    #     to_type = str(relationship.type).lower().split("_")[-1]

    # print(str(from_type))
    # print(to_type)
    # print(to_type == from_type.value)
 
    # return"ok"

    return relationship


def delete_relationship(relationship_id: int, db: Session):
    relationship = db.query(RelationshipModel).get(relationship_id)

    if not relationship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship ID is not found")
    
    db.delete(relationship)
    db.commit()
    
    return None



