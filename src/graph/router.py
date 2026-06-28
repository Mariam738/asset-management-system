from fastapi import APIRouter, Depends, status
from src.graph import controller
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.auth.model import UserModel
from src.utils.helpers import is_authenticated
from src.graph.dtos import GraphNode

graph_routes = APIRouter(prefix="/graph")

@graph_routes.get("", response_model=GraphNode, status_code=status.HTTP_200_OK,
                                          responses={404: {"description": "Not Found Error"}}
                  )
def get_graph(asset_id: str, db: Session = Depends(get_db), user:UserModel = Depends(is_authenticated)):
     return controller.get_graph(asset_id, db)