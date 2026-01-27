from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db
from src.schemas.score_response import PropertyWithScore
# Import the service
from src.api.services.property_service import PropertyService

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.get("/", response_model=List[PropertyWithScore])
def list_properties_with_scores(
    market: Optional[str] = Query(None, description="Filter by market area"),
    bedrooms: Optional[int] = Query(None, description="Filter by bedroom count"),
    min_revenue: Optional[float] = Query(None, description="Minimum revenue"),
    min_score: Optional[float] = Query(None, description="Minimum investment score"),
    sort_by: str = Query("total_score", description="Sort field"),
    order: str = Query("desc", description="Sort order"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Delegate logic to service
    return PropertyService.get_properties(
        db=db,
        market=market,
        bedrooms=bedrooms,
        min_revenue=min_revenue,
        min_score=min_score,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit
    )