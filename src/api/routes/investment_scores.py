from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Dict, Any
from src.database import get_db
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.schemas.score_response import (
    PropertyAnalysisResponse,
    ScoreBreakdown,
    MarketBenchmark
)

router = APIRouter(prefix="/properties", tags=["Analysis"])


@router.get("/{property_id}/analysis", response_model=PropertyAnalysisResponse)
def get_property_analysis(
    property_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed property analysis with:
    - Score breakdown
    - Market comparison
    - Comparable properties
    """
    # Fetch property with score
    property = db.query(Property).options(
        joinedload(Property.review_stats)
    ).filter(Property.property_id == property_id).first()
    
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")
    
    score = db.query(InvestmentScore).filter(
        InvestmentScore.property_id == property_id
    ).first()
    
    if not score:
        raise HTTPException(status_code=404, detail="Score not calculated for this property")
    
    # Get market comparison
    market_comparison = _get_market_comparison(db, property)
    
    # Get comparable properties
    comparable_properties = _get_comparable_properties(db, property, limit=5)
    
    # Build response
    return PropertyAnalysisResponse(
        property_id=property.property_id,
        title=property.title,
        market_area=property.market_area,
        bedrooms=property.bedrooms,
        bathrooms=property.bathrooms,
        property_type=property.property_type,
        revenue=float(property.revenue) if property.revenue else None,
        adr=float(property.adr) if property.adr else None,
        occupancy=property.occupancy,
        total_score=score.total_score,
        grade=score.grade,
        investment_tier=score.investment_tier,
        score_breakdown=ScoreBreakdown(
            revenue=score.revenue_score,
            occupancy=score.occupancy_score,
            positioning=score.positioning_score,
            reviews=score.review_score,
            amenities=score.amenity_score,
            host_status=score.host_status_score,
            seasonal=score.seasonal_score
        ),
        market_comparison=market_comparison,
        comparable_properties=comparable_properties
    )


def _get_market_comparison(db: Session, property: Property) -> Dict[str, Any]:
    """Calculate market averages for same bedroom count and market"""
    market_stats = db.query(
        func.avg(Property.revenue).label('avg_revenue'),
        func.avg(Property.adr).label('avg_adr'),
        func.avg(Property.occupancy).label('avg_occupancy'),
        func.avg(InvestmentScore.total_score).label('avg_score'),
        func.count(Property.property_id).label('property_count')
    ).join(
        InvestmentScore,
        Property.property_id == InvestmentScore.property_id
    ).filter(
        Property.market_area == property.market_area,
        Property.bedrooms == property.bedrooms
    ).first()
    
    if not market_stats:
        return None
    
    property_revenue = float(property.revenue) if property.revenue else 0
    property_adr = float(property.adr) if property.adr else 0
    
    return {
        'market_area': property.market_area,
        'bedroom_count': property.bedrooms,
        'market_avg_revenue': float(market_stats.avg_revenue or 0),
        'market_avg_adr': float(market_stats.avg_adr or 0),
        'market_avg_occupancy': float(market_stats.avg_occupancy or 0),
        'market_avg_score': float(market_stats.avg_score or 0),
        'property_count': market_stats.property_count,
        'revenue_vs_market': (property_revenue / float(market_stats.avg_revenue)) if market_stats.avg_revenue else 0,
        'adr_vs_market': (property_adr / float(market_stats.avg_adr)) if market_stats.avg_adr else 0,
        'score_vs_market': property.investment_score.total_score - float(market_stats.avg_score or 0) if hasattr(property, 'investment_score') else 0
    }


def _get_comparable_properties(
    db: Session,
    property: Property,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Find comparable properties in same market with similar specs"""
    comparables = db.query(Property, InvestmentScore).join(
        InvestmentScore,
        Property.property_id == InvestmentScore.property_id
    ).filter(
        Property.market_area == property.market_area,
        Property.bedrooms == property.bedrooms,
        Property.property_id != property.property_id
    ).order_by(
        InvestmentScore.total_score.desc()
    ).limit(limit).all()
    
    result = []
    for comp_prop, comp_score in comparables:
        result.append({
            'property_id': comp_prop.property_id,
            'title': comp_prop.title,
            'revenue': float(comp_prop.revenue) if comp_prop.revenue else None,
            'adr': float(comp_prop.adr) if comp_prop.adr else None,
            'occupancy': comp_prop.occupancy,
            'total_score': comp_score.total_score,
            'grade': comp_score.grade
        })
    
    return result