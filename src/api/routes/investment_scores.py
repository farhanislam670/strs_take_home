from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.score_response import PropertyAnalysisResponse
# Import the service
from src.api.services.analysis_service import AnalysisService

router = APIRouter(prefix="/properties", tags=["Analysis"])

@router.get("/{property_id}/analysis", response_model=PropertyAnalysisResponse)
def get_property_analysis(
    property_id: str,
    db: Session = Depends(get_db)
):
    # Delegate logic to service
    return AnalysisService.get_analysis(db, property_id)