from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from collections import defaultdict
from src.database import get_db
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.schemas.insight_response import (
    TopPerformersResponse,
    TopPerformer,
    MarketGroup,
    BedroomGroup
)

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/top-performers", response_model=TopPerformersResponse)
def get_top_performers(
    limit: int = Query(20, ge=1, le=100, description="Number of top properties"),
    db: Session = Depends(get_db)
):
    """
    Get top investment opportunities across all markets.
    Groups by market and bedroom category.
    Shows key differentiating factors.
    """
    # Get top properties
    top_properties_query = db.query(Property, InvestmentScore).join(
        InvestmentScore,
        Property.property_id == InvestmentScore.property_id
    ).order_by(
        InvestmentScore.total_score.desc()
    ).limit(limit).all()
    
    # Build top performers list
    top_performers = []
    by_market = defaultdict(list)
    by_bedroom = defaultdict(list)
    
    for prop, score in top_properties_query:
        # Identify key strengths
        strengths = _identify_strengths(prop, score)
        
        performer = TopPerformer(
            property_id=prop.property_id,
            title=prop.title,
            market_area=prop.market_area,
            bedrooms=prop.bedrooms,
            total_score=score.total_score,
            grade=score.grade,
            investment_tier=score.investment_tier,
            revenue=float(prop.revenue) if prop.revenue else None,
            revenue_vs_market=score.revenue_vs_market_avg,
            occupancy=prop.occupancy,
            adr=float(prop.adr) if prop.adr else None,
            key_strengths=strengths
        )
        
        top_performers.append(performer)
        by_market[prop.market_area].append(performer)
        if prop.bedrooms:
            by_bedroom[prop.bedrooms].append(performer)
    
    # Calculate market groups
    market_groups = []
    for market, properties in by_market.items():
        avg_score = sum(p.total_score for p in properties) / len(properties)
        market_groups.append(MarketGroup(
            market_area=market,
            property_count=len(properties),
            avg_score=round(avg_score, 2),
            top_properties=properties[:5]  # Top 5 per market
        ))
    
    # Calculate bedroom groups
    bedroom_groups = []
    for bedroom_count, properties in by_bedroom.items():
        avg_score = sum(p.total_score for p in properties) / len(properties)
        bedroom_groups.append(BedroomGroup(
            bedroom_count=bedroom_count,
            property_count=len(properties),
            avg_score=round(avg_score, 2),
            top_properties=properties[:5]  # Top 5 per bedroom count
        ))
    
    # Sort groups
    market_groups.sort(key=lambda x: x.avg_score, reverse=True)
    bedroom_groups.sort(key=lambda x: x.bedroom_count)
    
    return TopPerformersResponse(
        total_count=len(top_performers),
        top_properties=top_performers,
        by_market=market_groups,
        by_bedroom=bedroom_groups
    )


def _identify_strengths(property: Property, score: InvestmentScore) -> List[str]:
    """Identify key differentiating factors for a property"""
    strengths = []
    
    # High individual scores
    if score.revenue_score >= 85:
        strengths.append("Exceptional Revenue Performance")
    if score.occupancy_score >= 85:
        strengths.append("High Occupancy Consistency")
    if score.review_score >= 85:
        strengths.append("Outstanding Reviews")
    if score.amenity_score >= 85:
        strengths.append("Premium Amenities")
    
    # Host status
    if property.superhost:
        strengths.append("Superhost")
    if property.is_guest_favorite:
        strengths.append("Guest Favorite")
    
    # Revenue vs market
    if score.revenue_vs_market_avg and score.revenue_vs_market_avg > 1.5:
        strengths.append("150%+ Above Market Average")
    elif score.revenue_vs_market_avg and score.revenue_vs_market_avg > 1.25:
        strengths.append("Above Market Average")
    
    # Premium features
    if property.has_pool or property.system_pool:
        strengths.append("Pool")
    if property.has_waterfront:
        strengths.append("Waterfront")
    if property.system_view_ocean:
        strengths.append("Ocean View")
    
    return strengths[:5]  # Limit to top 5 strengths