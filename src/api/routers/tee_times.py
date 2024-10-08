from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, constr, validator
from enum import Enum

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class FilterParams(BaseModel):
    date: Optional[str] = Query(None)
    course: Optional[constr(max_length=100)] = None
    min_price: Optional[float] = Query(None, ge=0)
    max_price: Optional[float] = Query(None, ge=0)
    page: int = Query(1, ge=1)
    limit: int = Query(20, ge=1, le=100)
    sort_by: Optional[str] = Query(None, description="Field to sort by (e.g., 'datetime', 'price')")
    sort_order: SortOrder = Query(SortOrder.asc, description="Sort order (asc or desc)")

    @validator('date')
    def validate_date(cls, v):
        if v is None or v == '':
            return None
        try:
            return date.fromisoformat(v)
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD.')

from src.api.dependencies import get_db_session
from src.database.repositories.tee_time_repository import TeeTimeRepository

router = APIRouter()

@router.get("/all")
async def get_all_tee_times(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None, description="Field to sort by (e.g., 'datetime', 'price')"),
    sort_order: SortOrder = Query(SortOrder.asc, description="Sort order (asc or desc)"),
    db: Session = Depends(get_db_session)
):
    tee_time_repository = TeeTimeRepository(db)
    return tee_time_repository.get_all_tee_times(page, limit, sort_by, sort_order)

@router.get("/available")
async def get_all_available_tee_times(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Optional[str] = Query(None, description="Field to sort by (e.g., 'datetime', 'price')"),
    sort_order: SortOrder = Query(SortOrder.asc, description="Sort order (asc or desc)"),
    db: Session = Depends(get_db_session)
):
    tee_time_repository = TeeTimeRepository(db)
    return tee_time_repository.get_all_available_tee_times(page, limit, sort_by, sort_order)

@router.get("/filtered")
async def get_filtered_tee_times(
    params: FilterParams = Depends(),
    db: Session = Depends(get_db_session)
):
    if params.min_price is not None and params.max_price is not None and params.min_price > params.max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")
    
    tee_time_repository = TeeTimeRepository(db)
    return tee_time_repository.get_filtered_tee_times(
        params.date.isoformat() if params.date else None,
        params.course,
        params.min_price,
        params.max_price,
        params.page,
        params.limit,
        params.sort_by,
        params.sort_order
    )