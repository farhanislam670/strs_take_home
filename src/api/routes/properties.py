from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from src.database import get_db
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.schemas.score_response import PropertyWithScore

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.get("/", response_model=List[PropertyWithScore])
def list_properties_with_scores(
    market: Optional[str] = Query(None, description="Filter by market area"),
    bedrooms: Optional[int] = Query(None, description="Filter by bedroom count"),
    min_revenue: Optional[float] = Query(None, description="Minimum revenue"),
    min_score: Optional[float] = Query(None, description="Minimum investment score"),
    sort_by: str = Query("total_score", description="Sort field: total_score, revenue, occupancy"),
    order: str = Query("desc", description="Sort order: asc or desc"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    List all properties with their investment scores.
    Supports filtering, sorting, and pagination.
    """
    # Build query with join
    query = db.query(Property, InvestmentScore).join(
        InvestmentScore,
        Property.property_id == InvestmentScore.property_id
    )
    
    # Apply filters
    if market:
        query = query.filter(Property.market_area.ilike(f"%{market}%"))
    
    if bedrooms is not None:
        query = query.filter(Property.bedrooms == bedrooms)
    
    if min_revenue is not None:
        query = query.filter(Property.revenue >= min_revenue)
    
    if min_score is not None:
        query = query.filter(InvestmentScore.total_score >= min_score)
    
    # Apply sorting
    sort_column = {
        'total_score': InvestmentScore.total_score,
        'revenue': Property.revenue,
        'occupancy': Property.occupancy,
        'grade': InvestmentScore.grade
    }.get(sort_by, InvestmentScore.total_score)
    
    if order.lower() == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Pagination
    results = query.offset(skip).limit(limit).all()
    
    # Transform to response model
    response = []
    for prop, score in results:
        response.append(PropertyWithScore(
            property_id=prop.property_id,
            title=prop.title,
            market_area=prop.market_area,
            bedrooms=prop.bedrooms,
            property_type=prop.property_type,
            revenue=float(prop.revenue) if prop.revenue else None,
            adr=float(prop.adr) if prop.adr else None,
            occupancy=prop.occupancy,
            total_score=score.total_score,
            grade=score.grade,
            investment_tier=score.investment_tier,
            is_top_opportunity=score.is_top_opportunity
        ))
    
    return response