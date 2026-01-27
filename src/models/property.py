from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Integer, Float, Text, Boolean, Index, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from datetime import datetime

if TYPE_CHECKING:
    from src.models.amenities import PropertyAmenity
    from src.models.reviews import PropertyReview
    from src.models.investment_score import InvestmentScore

class Property(Base):
    __tablename__ = "properties"
    
    # External IDs
    property_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, primary_key=True)
    property_manager_host_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Basic Info
    title: Mapped[Optional[str]] = mapped_column(Text)
    market_area: Mapped[str] = mapped_column(String(100), index=True)
    property_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Location
    city_name: Mapped[Optional[str]] = mapped_column(String(100))
    state_name: Mapped[Optional[str]] = mapped_column(String(100))
    zipcode: Mapped[Optional[int]] = mapped_column(Integer)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    # URLs
    airbnb_host_url: Mapped[Optional[str]] = mapped_column(Text)
    airbnb_listing_url: Mapped[Optional[str]] = mapped_column(Text)
    vrbo_listing_url: Mapped[Optional[str]] = mapped_column(Text)

    # Host Status
    superhost: Mapped[bool] = mapped_column(Boolean, default=False)
    is_guest_favorite: Mapped[bool] = mapped_column(Boolean, default=False)

    # Booking Details
    minimum_stay: Mapped[Optional[int]] = mapped_column(Integer)
    available_nights: Mapped[Optional[int]] = mapped_column(Integer)
    occupancy: Mapped[Optional[float]] = mapped_column(Float)
    instant_book: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Physical Specs
    bedrooms: Mapped[Optional[int]] = mapped_column(Integer)
    bathrooms: Mapped[Optional[float]] = mapped_column(Float)
    number_of_beds: Mapped[Optional[int]] = mapped_column(Integer)
    accommodates: Mapped[Optional[int]] = mapped_column(Integer)
    person_capacity: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Financials
    price_tier: Mapped[Optional[str]] = mapped_column(String(50))
    revenue: Mapped[Optional[Decimal]] = mapped_column(Float(asdecimal=True))
    revenue_potential: Mapped[Optional[Decimal]] = mapped_column(Float(asdecimal=True))
    adr: Mapped[Optional[Decimal]] = mapped_column(Float(asdecimal=True))
    cleaning_fee: Mapped[Optional[Decimal]] = mapped_column(Float(asdecimal=True))

    # Ratings & Reviews
    property_reviews: Mapped[Optional[int]] = mapped_column(Integer)
    property_rating: Mapped[Optional[int]] = mapped_column(Integer)
    stars: Mapped[Optional[float]] = mapped_column(Float)

    # Data Quality
    data_quality_category: Mapped[Optional[str]] = mapped_column(String(50))
    quality_rating_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Basic Amenities (HAS_*)
    has_aircon: Mapped[bool] = mapped_column(Boolean, default=False)
    has_gym: Mapped[bool] = mapped_column(Boolean, default=False)
    has_hottub: Mapped[bool] = mapped_column(Boolean, default=False)
    has_kitchen: Mapped[bool] = mapped_column(Boolean, default=False)
    has_parking: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pets_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    has_pool: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # System Amenities (SYSTEM_*)
    system_gym: Mapped[bool] = mapped_column(Boolean, default=False)
    system_pool_table: Mapped[bool] = mapped_column(Boolean, default=False)
    system_arcade_machine: Mapped[bool] = mapped_column(Boolean, default=False)
    system_movie: Mapped[bool] = mapped_column(Boolean, default=False)
    system_bowling: Mapped[bool] = mapped_column(Boolean, default=False)
    system_chess: Mapped[bool] = mapped_column(Boolean, default=False)
    system_golf: Mapped[bool] = mapped_column(Boolean, default=False)
    system_crib: Mapped[bool] = mapped_column(Boolean, default=False)
    system_pack_n_play: Mapped[bool] = mapped_column(Boolean, default=False)
    system_play_slide: Mapped[bool] = mapped_column(Boolean, default=False)
    system_firepit: Mapped[bool] = mapped_column(Boolean, default=False)
    system_grill: Mapped[bool] = mapped_column(Boolean, default=False)
    system_pool: Mapped[bool] = mapped_column(Boolean, default=False)
    system_jacuzzi: Mapped[bool] = mapped_column(Boolean, default=False)
    system_view_ocean: Mapped[bool] = mapped_column(Boolean, default=False)
    system_view_mountain: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Outdoor Amenities
    has_outdoor_furniture: Mapped[bool] = mapped_column(Boolean, default=False)
    has_waterfront: Mapped[bool] = mapped_column(Boolean, default=False)
    has_lake_access: Mapped[bool] = mapped_column(Boolean, default=False)
    has_beach_access: Mapped[bool] = mapped_column(Boolean, default=False)
    has_outdoor_dining_area: Mapped[bool] = mapped_column(Boolean, default=False)

    # High Season Insights
    high_season_insights: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    amenity_data: Mapped["PropertyAmenity"] = relationship(
        "PropertyAmenity", back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    review_stats: Mapped["PropertyReview"] = relationship(
        "PropertyReview", back_populates="property", uselist=False, cascade="all, delete-orphan"
    )
    investment_score: Mapped["InvestmentScore"] = relationship( 
        "InvestmentScore", back_populates="property",  uselist=False,  cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index(
            "idx_properties_market_bedrooms_revenue",
            "market_area", "bedrooms", "revenue",
            postgresql_where=(bedrooms.isnot(None) & revenue.isnot(None)),
            postgresql_using="btree"
        ),
        Index(
            "idx_properties_analytics",
            "market_area", "bedrooms", "revenue", "occupancy", "adr",
            postgresql_where=(bedrooms.isnot(None) & revenue.isnot(None)),
            postgresql_using="btree"
        ),
        Index(
            "idx_properties_bedrooms",
            "bedrooms",
            postgresql_where=(bedrooms.isnot(None)),
            postgresql_using="btree"
        ),
        Index(
            "idx_properties_revenue",
            "revenue",
            postgresql_where=(revenue.isnot(None)),
            postgresql_using="btree"
        ),
    )