from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.insight_response import TopPerformersResponse
# Import the service
from src.api.services.insight_service import InsightService

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("/top-performers", response_model=TopPerformersResponse)
def get_top_performers(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Delegate logic to service
    return InsightService.get_top_performers(db, limit)