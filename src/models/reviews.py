from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, Float, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

if TYPE_CHECKING:
    from src.models.property import Property

class PropertyReview(Base):
    __tablename__ = "property_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("properties.property_id"), 
        unique=True
    )

    # General Stats
    review_total_reviews: Mapped[Optional[int]] = mapped_column(Integer)
    review_months_overall: Mapped[Optional[int]] = mapped_column(Integer)
    review_months_with_reviews: Mapped[Optional[int]] = mapped_column(Integer)
    review_months_without_reviews_overall: Mapped[Optional[int]] = mapped_column(Integer)
    review_avg_reviews_per_month: Mapped[Optional[float]] = mapped_column(Float)
    
    # High Season
    review_high_season_quarter: Mapped[Optional[int]] = mapped_column(Integer)
    review_high_season_reviews: Mapped[Optional[int]] = mapped_column(Integer)
    review_high_season_label: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Demographics / Categories
    review_count_stayed_with_kids: Mapped[Optional[int]] = mapped_column(Integer)
    review_pct_stayed_with_kids: Mapped[Optional[float]] = mapped_column(Float)
    
    review_count_group_trip: Mapped[Optional[int]] = mapped_column(Integer)
    review_pct_group_trip: Mapped[Optional[float]] = mapped_column(Float)
    
    review_count_stayed_with_a_pet: Mapped[Optional[int]] = mapped_column(Integer)
    review_pct_stayed_with_a_pet: Mapped[Optional[float]] = mapped_column(Float)
    
    review_missing_months_trailing_12: Mapped[Optional[int]] = mapped_column(Integer)

    # Link back
    property: Mapped["Property"] = relationship("Property", back_populates="review_stats")