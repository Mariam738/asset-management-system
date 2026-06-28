from typing import Generic, TypeVar, List
from pydantic import BaseModel


T = TypeVar('T')

# Use in bulking (maybe in future extend to bulk edit and delete)
class ApiResponse(BaseModel, Generic[T]):
    status: str
    message: str
    data: T | None = None

class PaginationResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    count: int
    data: List[T]