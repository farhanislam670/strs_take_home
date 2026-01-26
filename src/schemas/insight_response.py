from pydantic import BaseModel
from typing import List, Dict, Optional


class TopPerformer(BaseModel):
    """Top performing property summary"""
    property_id: str
    title: Optional[str]
    market_area: str
    bedrooms: Optional[int]
    total_score: float
    grade: str
    investment_tier: str
    
    # Key metrics
    revenue: Optional[float]
    revenue_vs_market: Optional[float]  # Ratio
    occupancy: Optional[float]
    adr: Optional[float]
    
    # Differentiating factors
    key_strengths: List[str]
    
    class Config:
        from_attributes = True


class MarketGroup(BaseModel):
    """Properties grouped by market"""
    market_area: str
    property_count: int
    avg_score: float
    top_properties: List[TopPerformer]


class BedroomGroup(BaseModel):
    """Properties grouped by bedroom count"""
    bedroom_count: int
    property_count: int
    avg_score: float
    top_properties: List[TopPerformer]


class TopPerformersResponse(BaseModel):
    """Response for top performers endpoint"""
    total_count: int
    top_properties: List[TopPerformer]
    by_market: List[MarketGroup]
    by_bedroom: List[BedroomGroup]