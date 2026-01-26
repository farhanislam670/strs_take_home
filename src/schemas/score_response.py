from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class ScoreBreakdown(BaseModel):
    """Individual component scores"""
    revenue: float
    occupancy: float
    positioning: float
    reviews: float
    amenities: float
    host_status: float
    seasonal: float


class InvestmentScoreResponse(BaseModel):
    """Basic investment score info"""
    property_id: str
    total_score: float
    grade: str
    investment_tier: str
    is_top_opportunity: bool
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class PropertyAnalysisResponse(BaseModel):
    """Detailed property analysis with score breakdown"""
    # Property basics
    property_id: str
    title: Optional[str]
    market_area: str
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    property_type: Optional[str]
    
    # Financial
    revenue: Optional[float]
    adr: Optional[float]
    occupancy: Optional[float]
    
    # Score data
    total_score: float
    grade: str
    investment_tier: str
    score_breakdown: ScoreBreakdown
    
    # Market comparison
    market_comparison: Optional[Dict] = None
    comparable_properties: Optional[List[Dict]] = None
    
    class Config:
        from_attributes = True


class MarketBenchmark(BaseModel):
    """Market average data for comparison"""
    market_area: str
    bedroom_count: int
    avg_revenue: float
    avg_adr: float
    avg_occupancy: float
    property_count: int
    avg_score: float


class PropertyWithScore(BaseModel):
    """Property listing with score"""
    property_id: str
    title: Optional[str]
    market_area: str
    bedrooms: Optional[int]
    property_type: Optional[str]
    revenue: Optional[float]
    adr: Optional[float]
    occupancy: Optional[float]
    total_score: float
    grade: str
    investment_tier: str
    is_top_opportunity: bool
    
    class Config:
        from_attributes = True