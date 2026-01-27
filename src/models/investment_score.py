from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

if TYPE_CHECKING:
    from src.models.property import Property

class InvestmentScore(Base):
    __tablename__ = "investment_scores"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("properties.property_id"),
        unique=True,
        index=True
    )
    
    # Overall Score
    total_score: Mapped[float] = mapped_column(Float)
    grade: Mapped[str] = mapped_column(String(10))  # A+, A, B+, etc.
    investment_tier: Mapped[str] = mapped_column(String(50))  # PRIME, STRONG, etc.
    
    # Individual Component Scores
    revenue_score: Mapped[float] = mapped_column(Float)
    occupancy_score: Mapped[float] = mapped_column(Float)
    positioning_score: Mapped[float] = mapped_column(Float)
    review_score: Mapped[float] = mapped_column(Float)
    amenity_score: Mapped[float] = mapped_column(Float)
    host_status_score: Mapped[float] = mapped_column(Float)
    seasonal_score: Mapped[float] = mapped_column(Float)
    
    # Market Context
    market_area: Mapped[str] = mapped_column(String(100), index=True)
    bedroom_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Revenue Metrics
    revenue_vs_market_avg: Mapped[Optional[float]] = mapped_column(Float)  # Ratio
    revenue_potential_gap: Mapped[Optional[float]] = mapped_column(Float)  # Percentage
    
    # Detailed Breakdown (JSON for flexibility)
    score_breakdown: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # Flags
    is_top_opportunity: Mapped[bool] = mapped_column(default=False)
    
    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationship
    property: Mapped["Property"] = relationship("Property", back_populates="investment_score")