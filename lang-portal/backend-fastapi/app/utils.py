from typing import TypeVar, Generic, List, Optional, Dict, Any
from fastapi import HTTPException, Query
from pydantic import BaseModel, conint

# Generic type for items
T = TypeVar('T')

class PaginationParams:
    """
    Pagination parameters that can be used as FastAPI dependencies.
    Usage:
        @app.get("/items")
        async def get_items(pagination: PaginationParams = Depends()):
            ...
    """
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        items_per_page: int = Query(100, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.items_per_page = items_per_page

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model.
    Usage:
        response_model=PaginatedResponse[ItemModel]
    """
    items: List[T]
    pagination: Dict[str, int]

def create_paginated_response(
    items: List[T],
    total_count: int,
    pagination: PaginationParams
) -> Dict[str, Any]:
    """
    Creates a standardized paginated response.
    Args:
        items: List of items for current page
        total_count: Total number of items across all pages
        pagination: Pagination parameters
    Returns:
        Dictionary with items and pagination info
    """
    total_pages = (total_count + pagination.items_per_page - 1) // pagination.items_per_page
    
    return {
        "items": items,
        "pagination": {
            "current_page": pagination.page,
            "total_pages": total_pages,
            "total_items": total_count,
            "items_per_page": pagination.items_per_page
        }
    }

def validate_entity_exists(entity: Optional[Any], entity_name: str) -> None:
    """
    Validates that an entity exists, raises HTTPException if not.
    Args:
        entity: Entity to check
        entity_name: Name of entity for error message
    Raises:
        HTTPException: If entity doesn't exist
    """
    if not entity:
        raise HTTPException(
            status_code=404,
            detail=f"{entity_name} not found"
        )

class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str

def create_success_response(
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Creates a standardized success response.
    Args:
        message: Success message
        data: Optional data to include
    Returns:
        Success response dictionary
    """
    response = {
        "success": True,
        "message": message
    }
    if data:
        response.update(data)
    return response 