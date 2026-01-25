from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal


class PropertyCSVRow(BaseModel):
    """Raw CSV row - matches CSV column names exactly."""
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)
    
    # External IDs
    property_id: str = Field(alias="Property ID")
    property_manager_host_id: Optional[str] = Field(None, alias="Property Manager/ Host ID")
    
    # Basic Info
    title: Optional[str] = Field(None, alias="TITLE")
    listing_name: Optional[str] = Field(None, alias="Listing Name")
    name: Optional[str] = Field(None, alias="name")
    
    # Location
    city_name: Optional[str] = Field(None, alias="CITY_NAME")
    state_name: Optional[str] = Field(None, alias="STATE_NAME")
    zipcode: Optional[int] = Field(None, alias="ZIPCODE")
    latitude: Optional[float] = Field(None, alias="LATITUDE")
    longitude: Optional[float] = Field(None, alias="LONGITUDE")
    
    # URLs
    airbnb_host_url: Optional[str] = Field(None, alias="Airbnb Host URL")
    airbnb_listing_url: Optional[str] = Field(None, alias="Airbnb Listing URL")
    vrbo_listing_url: Optional[str] = Field(None, alias="Vrbo Listing URL")
    url: Optional[str] = Field(None, alias="url")
    
    # Physical Specs
    bedrooms: Optional[int] = Field(None, alias="BEDROOMS")
    bathrooms: Optional[Decimal] = Field(None, alias="BATHROOMS")
    baths: Optional[str] = Field(None, alias="baths")  # needs cleaning
    number_of_beds: Optional[int] = Field(None, alias="number_of_beds")
    beds: Optional[str] = Field(None, alias="beds")
    accommodates: Optional[int] = Field(None, alias="ACCOMMODATES")
    person_capacity: Optional[int] = Field(None, alias="personCapacity")
    number_of_guests: Optional[str] = Field(None, alias="numberOfGuests")  # needs cleaning
    
    # Property Type
    property_type: Optional[str] = Field(None, alias="propertyType")
    room_type: Optional[str] = Field(None, alias="roomType")
    
    # Description
    description: Optional[str] = Field(None, alias="description")
    
    # Booking
    minimum_stay: Optional[int] = Field(None, alias="MINIMUM_STAY")
    available_nights: Optional[int] = Field(None, alias="Available Nights")
    occupancy: Optional[float] = Field(None, alias="Occupancy")
    instant_book: Optional[bool] = Field(False, alias="INSTANT_BOOK")
    
    # Financials
    price_tier: Optional[str] = Field(None, alias="PRICE_TIER")
    revenue: Optional[float] = Field(None, alias="Revenue")
    revenue_potential: Optional[float] = Field(None, alias="Revenue Potential")
    adr: Optional[float] = Field(None, alias="ADR")
    cleaning_fee: Optional[float] = Field(None, alias="Cleaning Fee")
    
    # Ratings
    property_reviews: Optional[int] = Field(None, alias="Property Reviews")
    property_rating: Optional[float] = Field(None, alias="Property Rating")
    stars: Optional[float] = Field(None, alias="stars")
    reviews_count: Optional[int] = Field(None, alias="reviewsCount")
    
    # Data Quality
    data_quality_category: Optional[str] = Field(None, alias="Data Quality Category")
    quality_rating_reason: Optional[str] = Field(None, alias="Quality Rating Reason")
    error_reason: Optional[str] = Field(None, alias="error_reason")
    
    # Host Status
    superhost: Optional[bool] = Field(False, alias="SUPERHOST")
    is_super_host: Optional[bool] = Field(False, alias="is_super_host")
    is_guest_favorite: Optional[bool] = Field(False, alias="is_guest_favorite")
    
    # Basic Amenities
    has_aircon: Optional[bool] = Field(False, alias="HAS_AIRCON")
    has_gym: Optional[bool] = Field(False, alias="HAS_GYM")
    has_hottub: Optional[bool] = Field(False, alias="HAS_HOTTUB")
    has_kitchen: Optional[bool] = Field(False, alias="HAS_KITCHEN")
    has_parking: Optional[bool] = Field(False, alias="HAS_PARKING")
    has_pets_allowed: Optional[bool] = Field(False, alias="HAS_PETS_ALLOWED")
    has_pool: Optional[bool] = Field(False, alias="HAS_POOL")
    
    # System Amenities
    system_gym: Optional[bool] = Field(False, alias="SYSTEM_GYM")
    system_pool_table: Optional[bool] = Field(False, alias="SYSTEM_POOL_TABLE")
    system_arcade_machine: Optional[bool] = Field(False, alias="SYSTEM_ARCADE_MACHINE")
    system_movie: Optional[bool] = Field(False, alias="SYSTEM_MOVIE")
    system_bowling: Optional[bool] = Field(False, alias="SYSTEM_BOWLING")
    system_chess: Optional[bool] = Field(False, alias="SYSTEM_CHESS")
    system_golf: Optional[bool] = Field(False, alias="SYSTEM_GOLF")
    system_crib: Optional[bool] = Field(False, alias="SYSTEM_CRIB")
    system_pack_n_play: Optional[bool] = Field(False, alias="SYSTEM_PACK_N_PLAY")
    system_play_slide: Optional[bool] = Field(False, alias="SYSTEM_PLAY_SLIDE")
    system_firepit: Optional[bool] = Field(False, alias="SYSTEM_FIREPIT")
    system_grill: Optional[bool] = Field(False, alias="SYSTEM_GRILL")
    system_pool: Optional[bool] = Field(False, alias="SYSTEM_POOL")
    system_jacuzzi: Optional[bool] = Field(False, alias="SYSTEM_JACUZZI")
    system_view_ocean: Optional[bool] = Field(False, alias="SYSTEM_VIEW_OCEAN")
    system_view_mountain: Optional[bool] = Field(False, alias="SYSTEM_VIEW_MOUNTAIN")
    
    # Outdoor Amenities
    has_outdoor_furniture: Optional[bool] = Field(False, alias="Has_Outdoor_Furniture")
    has_waterfront: Optional[bool] = Field(False, alias="Has_Waterfront")
    has_lake_access: Optional[bool] = Field(False, alias="Has_Lake_Access")
    has_beach_access: Optional[bool] = Field(False, alias="Has_Beach_Access")
    has_outdoor_dining_area: Optional[bool] = Field(False, alias="Has_Outdoor_Dining_Area")
    
    # Amenities List
    amenities: Optional[str] = Field(None, alias="amenities")
    
    # Review Metrics
    review_total_reviews: Optional[int] = Field(None, alias="review_total_reviews")
    total_reviews: Optional[int] = Field(None, alias="total_reviews")
    review_months_overall: Optional[int] = Field(None, alias="review_months_overall")
    total_months: Optional[int] = Field(None, alias="total_months")
    review_months_with_reviews: Optional[int] = Field(None, alias="review_months_with_reviews")
    review_months_without_reviews_overall: Optional[int] = Field(None, alias="review_months_without_reviews_overall")
    missing_months: Optional[int] = Field(None, alias="missing_months")
    review_avg_reviews_per_month: Optional[float] = Field(None, alias="review_avg_reviews_per_month")
    avg_reviews_per_month: Optional[float] = Field(None, alias="avg_reviews_per_month")
    review_high_season_quarter: Optional[int] = Field(None, alias="review_high_season_quarter")
    high_season: Optional[int] = Field(None, alias="high_season")
    review_high_season_reviews: Optional[int] = Field(None, alias="review_high_season_reviews")
    high_season_reviews: Optional[int] = Field(None, alias="high_season_reviews")
    review_high_season_label: Optional[str] = Field(None, alias="review_high_season_label")
    high_season_insights: Optional[str] = Field(None, alias="High Season Insights")
    review_count_stayed_with_kids: Optional[int] = Field(None, alias="review_count_stayed_with_kids")
    review_pct_stayed_with_kids: Optional[float] = Field(None, alias="review_pct_stayed_with_kids")
    review_count_group_trip: Optional[int] = Field(None, alias="review_count_group_trip")
    review_pct_group_trip: Optional[float] = Field(None, alias="review_pct_group_trip")
    review_count_stayed_with_a_pet: Optional[int] = Field(None, alias="review_count_stayed_with_a_pet")
    review_pct_stayed_with_a_pet: Optional[float] = Field(None, alias="review_pct_stayed_with_a_pet")
    review_missing_months_trailing_12: Optional[int] = Field(None, alias="review_missing_months_trailing_12")


class CleanedPropertyData(BaseModel):
    """Cleaned and transformed data ready for database."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Property data
    property_id: str
    property_manager_host_id: Optional[str] = None
    title: Optional[str] = None
    market_area: str
    property_type: Optional[str] = None
    description: Optional[str] = None
    
    city_name: Optional[str] = None
    state_name: Optional[str] = None
    zipcode: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    airbnb_host_url: Optional[str] = None
    airbnb_listing_url: Optional[str] = None
    vrbo_listing_url: Optional[str] = None
    
    minimum_stay: Optional[int] = None
    available_nights: Optional[int] = None
    occupancy: Optional[float] = None
    instant_book: bool = False
    
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    number_of_beds: Optional[int] = None
    accommodates: Optional[int] = None
    person_capacity: Optional[int] = None
    
    price_tier: Optional[str] = None
    revenue: Optional[Decimal] = None
    revenue_potential: Optional[Decimal] = None
    adr: Optional[Decimal] = None
    cleaning_fee: Optional[Decimal] = None
    
    property_reviews: Optional[int] = None
    property_rating: Optional[float] = None
    stars: Optional[float] = None
    
    data_quality_category: Optional[str] = None
    quality_rating_reason: Optional[str] = None
    
    superhost: bool = False
    is_guest_favorite: bool = False
    
    # All boolean amenities
    has_aircon: bool = False
    has_gym: bool = False
    has_hottub: bool = False
    has_kitchen: bool = False
    has_parking: bool = False
    has_pets_allowed: bool = False
    has_pool: bool = False
    
    system_gym: bool = False
    system_pool_table: bool = False
    system_arcade_machine: bool = False
    system_movie: bool = False
    system_bowling: bool = False
    system_chess: bool = False
    system_golf: bool = False
    system_crib: bool = False
    system_pack_n_play: bool = False
    system_play_slide: bool = False
    system_firepit: bool = False
    system_grill: bool = False
    system_pool: bool = False
    system_jacuzzi: bool = False
    system_view_ocean: bool = False
    system_view_mountain: bool = False
    
    has_outdoor_furniture: bool = False
    has_waterfront: bool = False
    has_lake_access: bool = False
    has_beach_access: bool = False
    has_outdoor_dining_area: bool = False
    
    high_season_insights: Optional[str] = None
    
    # Separated data
    amenities_list: List[str] = Field(default_factory=list)
    
    # Review stats (for separate table)
    review_total_reviews: Optional[int] = None
    review_months_overall: Optional[int] = None
    review_months_with_reviews: Optional[int] = None
    review_months_without_reviews_overall: Optional[int] = None
    review_avg_reviews_per_month: Optional[float] = None
    review_high_season_quarter: Optional[int] = None
    review_high_season_reviews: Optional[int] = None
    review_high_season_label: Optional[str] = None
    review_count_stayed_with_kids: Optional[int] = None
    review_pct_stayed_with_kids: Optional[float] = None
    review_count_group_trip: Optional[int] = None
    review_pct_group_trip: Optional[float] = None
    review_count_stayed_with_a_pet: Optional[int] = None
    review_pct_stayed_with_a_pet: Optional[float] = None
    review_missing_months_trailing_12: Optional[int] = None