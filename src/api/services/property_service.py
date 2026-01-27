from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.schemas.score_response import PropertyWithScore

class PropertyService:
    @staticmethod
    def get_properties(
        db: Session,
        market: Optional[str] = None,
        bedrooms: Optional[int] = None,
        min_revenue: Optional[float] = None,
        min_score: Optional[float] = None,
        sort_by: str = "total_score",
        order: str = "desc",
        skip: int = 0,
        limit: int = 50
    ) -> List[PropertyWithScore]:
        
        # Base Query
        query = db.query(Property, InvestmentScore).join(
            InvestmentScore,
            Property.property_id == InvestmentScore.property_id
        )

        # Filters
        if market:
            query = query.filter(Property.market_area.ilike(f"%{market}%"))
        if bedrooms is not None:
            query = query.filter(Property.bedrooms == bedrooms)
        if min_revenue is not None:
            query = query.filter(Property.revenue >= min_revenue)
        if min_score is not None:
            query = query.filter(InvestmentScore.total_score >= min_score)

        # Sorting
        sort_map = {
            'total_score': InvestmentScore.total_score,
            'revenue': Property.revenue,
            'occupancy': Property.occupancy,
            'grade': InvestmentScore.grade
        }
        sort_col = sort_map.get(sort_by, InvestmentScore.total_score)
        
        if order.lower() == 'desc':
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())

        # Execution
        results = query.offset(skip).limit(limit).all()

        # Transformation
        return [
            PropertyWithScore(
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
            ) for prop, score in results
        ]