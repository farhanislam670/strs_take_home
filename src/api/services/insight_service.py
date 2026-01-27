from sqlalchemy.orm import Session
from collections import defaultdict
from typing import List
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.schemas.insight_response import TopPerformersResponse, TopPerformer, MarketGroup, BedroomGroup

class InsightService:
    @staticmethod
    def get_top_performers(db: Session, limit: int) -> TopPerformersResponse:
        # Fetch Data
        top_props = db.query(Property, InvestmentScore).join(
            InvestmentScore
        ).order_by(InvestmentScore.total_score.desc()).limit(limit).all()

        # Process Data
        top_performers = []
        by_market = defaultdict(list)
        by_bedroom = defaultdict(list)

        for prop, score in top_props:
            strengths = InsightService._identify_strengths(prop, score)
            
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

        return TopPerformersResponse(
            total_count=len(top_performers),
            top_properties=top_performers,
            by_market=InsightService._build_market_groups(by_market),
            by_bedroom=InsightService._build_bedroom_groups(by_bedroom)
        )

    @staticmethod
    def _identify_strengths(property: Property, score: InvestmentScore) -> List[str]:
        strengths = []
        if score.revenue_score >= 85: strengths.append("Exceptional Revenue Performance")
        if score.occupancy_score >= 85: strengths.append("High Occupancy Consistency")
        if score.review_score >= 85: strengths.append("Outstanding Reviews")
        if score.amenity_score >= 85: strengths.append("Premium Amenities")
        if property.superhost: strengths.append("Superhost")
        if property.is_guest_favorite: strengths.append("Guest Favorite")
        
        if score.revenue_vs_market_avg and score.revenue_vs_market_avg > 1.5:
            strengths.append("150%+ Above Market Average")
        elif score.revenue_vs_market_avg and score.revenue_vs_market_avg > 1.25:
            strengths.append("Above Market Average")
            
        if property.has_pool or property.system_pool: strengths.append("Pool")
        if property.has_waterfront: strengths.append("Waterfront")
        
        return strengths[:5]

    @staticmethod
    def _build_market_groups(grouped_data):
        groups = []
        for market, props in grouped_data.items():
            avg = sum(p.total_score for p in props) / len(props)
            groups.append(MarketGroup(
                market_area=market,
                property_count=len(props),
                avg_score=round(avg, 2),
                top_properties=props[:5]
            ))
        return sorted(groups, key=lambda x: x.avg_score, reverse=True)

    @staticmethod
    def _build_bedroom_groups(grouped_data):
        groups = []
        for beds, props in grouped_data.items():
            avg = sum(p.total_score for p in props) / len(props)
            groups.append(BedroomGroup(
                bedroom_count=beds,
                property_count=len(props),
                avg_score=round(avg, 2),
                top_properties=props[:5]
            ))
        return sorted(groups, key=lambda x: x.bedroom_count)