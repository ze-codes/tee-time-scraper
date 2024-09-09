from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, time
from typing import List, Optional

from src.api.dependencies import get_db_session
from src.database.repositories.tee_time_repository import TeeTimeRepository

router = APIRouter()

@router.get("/")
async def get_tee_times(
    starttime: time = Query(None),
    endtime: time = Query(None),
    course: Optional[List[str]] = Query(None),
    distance: Optional[str] = Query(None),
    availability: Optional[int] = Query(None),
    startage: Optional[int] = Query(None),
    endage: Optional[int] = Query(None),
    gender: Optional[str] = Query(None),
    race: Optional[str] = Query(None),
    socialLevel: Optional[str] = Query(None),
    handicap: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("time"),
    order: str = Query("asc"),
    db: Session = Depends(get_db_session)
):
    tee_time_repository = TeeTimeRepository(db)
    
    filters = {
        "starttime": datetime.combine(datetime.now().date(), starttime) if starttime else None,
        "endtime": datetime.combine(datetime.now().date(), endtime) if endtime else None,
        "course": course,
        "distance": distance,
        "availability": availability,
        "startage": startage,
        "endage": endage,
        "gender": gender,
        "race": race,
        "socialLevel": socialLevel,
        "handicap": handicap
    }
    
    return tee_time_repository.get_tee_times(filters, page, limit, sort, order)