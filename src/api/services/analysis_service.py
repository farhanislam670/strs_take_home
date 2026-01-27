from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException
from typing import Dict, Any, List
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.schemas.score_response import PropertyAnalysisResponse, ScoreBreakdown

class AnalysisService:
    @staticmethod
    def get_analysis(db: Session, property_id: str) -> PropertyAnalysisResponse:
        property = db.query(Property).options(
            joinedload(Property.review_stats)
        ).filter(Property.property_id == property_id).first()

        print(property)

        if not property:
            raise HTTPException(status_code=404, detail="Property not found")

        score = db.query(InvestmentScore).filter(
            InvestmentScore.property_id == property_id
        ).first()

        print(score)

        if not score:
            raise HTTPException(status_code=404, detail="Score not calculated for this property")

        market_comparison = AnalysisService._get_market_comparison(db, property)
        comparables = AnalysisService._get_comparable_properties(db, property)

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
            comparable_properties=comparables
        )

    @staticmethod
    def _get_market_comparison(db: Session, property: Property) -> Dict[str, Any]:
        market_stats = db.query(
            func.avg(Property.revenue).label('avg_revenue'),
            func.avg(Property.adr).label('avg_adr'),
            func.avg(Property.occupancy).label('avg_occupancy'),
            func.avg(InvestmentScore.total_score).label('avg_score'),
            func.count(Property.property_id).label('property_count')
        ).join(InvestmentScore).filter(
            Property.market_area == property.market_area,
            Property.bedrooms == property.bedrooms
        ).first()

        if not market_stats:
            return None

        prop_rev = float(property.revenue or 0)
        prop_adr = float(property.adr or 0)

        return {
            'market_area': property.market_area,
            'bedroom_count': property.bedrooms,
            'market_avg_revenue': float(market_stats.avg_revenue or 0),
            'market_avg_adr': float(market_stats.avg_adr or 0),
            'market_avg_occupancy': float(market_stats.avg_occupancy or 0),
            'market_avg_score': float(market_stats.avg_score or 0),
            'property_count': market_stats.property_count,
            'revenue_vs_market': (prop_rev / float(market_stats.avg_revenue)) if market_stats.avg_revenue else 0,
            'adr_vs_market': (prop_adr / float(market_stats.avg_adr)) if market_stats.avg_adr else 0,
            'score_vs_market': property.investment_score.total_score - float(market_stats.avg_score or 0) if hasattr(property, 'investment_score') else 0
        }

    @staticmethod
    def _get_comparable_properties(db: Session, property: Property, limit: int = 5) -> List[Dict[str, Any]]:
        comparables = db.query(Property, InvestmentScore).join(
            InvestmentScore
        ).filter(
            Property.market_area == property.market_area,
            Property.bedrooms == property.bedrooms,
            Property.property_id != property.property_id
        ).order_by(InvestmentScore.total_score.desc()).limit(limit).all()

        return [{
            'property_id': p.property_id,
            'title': p.title,
            'revenue': float(p.revenue) if p.revenue else None,
            'adr': float(p.adr) if p.adr else None,
            'occupancy': p.occupancy,
            'total_score': s.total_score,
            'grade': s.grade
        } for p, s in comparables]