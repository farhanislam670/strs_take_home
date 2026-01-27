import re
from typing import Optional, List
from decimal import Decimal
from src.schemas.property_csv import PropertyCSVRow, CleanedPropertyData
import logging
import re
import unicodedata

logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and transforms raw CSV data."""
    
    @staticmethod
    def clean_number_string(value: Optional[str]) -> Optional[int]:
        """
        Clean strings like '4 guests' -> 4, '2 baths' -> 2
        """
        if not value:
            return None
        
        if isinstance(value, (int, float)):
            return int(value)
            
        # Extract first number from string
        match = re.search(r'\d+', str(value))
        if match:
            return int(match.group())
        
        return None
    
    @staticmethod
    def clean_occupancy(value: Optional[float]) -> Optional[float]:
        """Ensure occupancy is between 0 and 1."""
        if value is None:
            return None
        
        # If value is percentage (> 1), convert to decimal
        if value > 1:
            value = value / 100
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, value))
    
    @staticmethod
    def clean_stars(value: Optional[float]) -> Optional[float]:
        """Ensure stars rating is between 0 and 5."""
        if value is None:
            return None
        
        return max(0.0, min(5.0, value))
    
    @staticmethod
    def clean_price_tier(value: Optional[str]) -> Optional[str]:
        """
        Clean price tier strings by removing numbering.
        
        Examples:
            "1. Budget" -> "Budget"
            "5. Luxury" -> "Luxury"
            "No Tier" -> None
            "3. Midscale" -> "Midscale"
        
        Returns None for invalid/empty values.
        """
        if not value:
            return None
        
        value_str = str(value).strip()
        
        # Handle "No Tier" case
        if value_str.lower() in ['no tier', 'none', '']:
            return None
        
        # Remove numbering pattern: "1. ", "2. ", etc.
        cleaned = re.sub(r'^\d+\.\s*', '', value_str)
        
        # Validate against known tiers
        valid_tiers = ['Budget', 'Economy', 'Midscale', 'Upscale', 'Luxury']
        
        if cleaned in valid_tiers:
            return cleaned
        
        # Log warning for unexpected values
        logger.warning(f"Unexpected price tier value: '{value}' -> cleaned to '{cleaned}'")
        
        return cleaned if cleaned else None
    
    @staticmethod
    def parse_amenities(amenities_str: Optional[str]) -> List[str]:
        """
        Parse comma-separated amenities string into list.
        
        Example: "WiFi, Kitchen, Pool" -> ["WiFi", "Kitchen", "Pool"]
        """
        if not amenities_str:
            return []
        
        # Split by comma and clean whitespace
        amenities = [a.strip() for a in str(amenities_str).split(',')]
        
        # Remove empty strings
        amenities = [a for a in amenities if a]
        
        return amenities

    @staticmethod
    def should_skip_row(csv_row: PropertyCSVRow) -> tuple[bool, str]:
        """
        Determine if a row should be skipped.
        
        Returns:
            (should_skip: bool, reason: str)
        """
        # Skip if error_reason is present and not empty
        if csv_row.error_reason and str(csv_row.error_reason).strip():
            return True, f"error_reason: {csv_row.error_reason}"
        
        # Add other skip conditions here if needed
        # For example:
        # if not csv_row.property_id:
        #     return True, "missing property_id"
        
        return False, ""
    


    @staticmethod
    def clean_title(title: str) -> str:
        if not title:
            return None
        
        # 1. Normalize Unicode (fixes weird accents/characters)
        title = unicodedata.normalize('NFKC', str(title))
        
        # 2. Replace separators (•, |, etc.) with a standard " - "
        # This regex looks for bullets, pipes, or middle dots surrounded by optional space
        title = re.sub(r'\s*[•|·]\s*', ' - ', title)
        
        # 3. (Optional) Remove Emojis/Symbols if you only want text/numbers/punctuation
        # This keeps alphanumeric, spaces, and basic punctuation (.,&!-)
        # title = re.sub(r'[^\w\s.,&!-]', '', title) 
        
        # 4. Collapse multiple spaces into one and strip ends
        title = re.sub(r'\s+', ' ', title)
        
        return title.strip()
    
    @staticmethod
    def resolve_duplicates(csv_row: PropertyCSVRow, market_area: str) -> CleanedPropertyData:
        """
        Resolve duplicate columns and create CleanedPropertyData.
        """
        
        # 1. Get the raw title
        raw_title = csv_row.title or csv_row.listing_name or csv_row.name
        
        # 2. Clean the title
        title = DataCleaner.clean_title(raw_title)
        
        # Superhost resolution (prefer SUPERHOST)
        superhost = csv_row.superhost or csv_row.is_super_host or False
        
        # Bathrooms resolution
        bathrooms = csv_row.bathrooms
        
        # Beds resolution
        number_of_beds = csv_row.number_of_beds
        
        # Person capacity resolution
        person_capacity = csv_row.person_capacity
        if person_capacity is None and csv_row.number_of_guests:
            person_capacity = DataCleaner.clean_number_string(csv_row.number_of_guests)
        if person_capacity is None:
            person_capacity = csv_row.accommodates
        
        # Review metrics resolution
        review_total = csv_row.review_total_reviews or csv_row.total_reviews or csv_row.property_reviews or csv_row.reviews_count
        review_months_overall = csv_row.review_months_overall or csv_row.total_months
        review_avg_per_month = csv_row.review_avg_reviews_per_month or csv_row.avg_reviews_per_month
        review_high_season_quarter = csv_row.review_high_season_quarter or csv_row.high_season
        review_high_season_reviews = csv_row.review_high_season_reviews or csv_row.high_season_reviews
        review_missing_trailing_12 = csv_row.review_missing_months_trailing_12
        if review_missing_trailing_12 is None and csv_row.missing_months is not None:
            # Only use first 12 months
            review_missing_trailing_12 = min(csv_row.missing_months, 12)
        
        # Property type resolution
        property_type = csv_row.property_type or csv_row.room_type
        
        # URL resolution (prefer specific over generic)
        url = csv_row.airbnb_listing_url or csv_row.url
        
        # Latitude/Longitude resolution
        latitude = csv_row.latitude or csv_row.longitude  # Try both aliases
        longitude = csv_row.longitude or csv_row.latitude
        
        # Parse amenities
        amenities_list = DataCleaner.parse_amenities(csv_row.amenities)
        
        # Clean price tier
        price_tier = DataCleaner.clean_price_tier(csv_row.price_tier)
        
        # Convert financials to Decimal
        revenue = Decimal(str(csv_row.revenue)) if csv_row.revenue is not None else None
        revenue_potential = Decimal(str(csv_row.revenue_potential)) if csv_row.revenue_potential is not None else None
        adr = Decimal(str(csv_row.adr)) if csv_row.adr is not None else None
        cleaning_fee = Decimal(str(csv_row.cleaning_fee)) if csv_row.cleaning_fee is not None else None
        
        return CleanedPropertyData(
            property_id=csv_row.property_id,
            property_manager_host_id=csv_row.property_manager_host_id,
            title=title,
            market_area=market_area,
            property_type=property_type,
            description=csv_row.description,
            
            city_name=csv_row.city_name,
            state_name=csv_row.state_name,
            zipcode=csv_row.zipcode,
            latitude=latitude,
            longitude=longitude,
            
            airbnb_host_url=csv_row.airbnb_host_url,
            airbnb_listing_url=url,
            vrbo_listing_url=csv_row.vrbo_listing_url,
            
            minimum_stay=csv_row.minimum_stay,
            available_nights=csv_row.available_nights,
            occupancy=DataCleaner.clean_occupancy(csv_row.occupancy),
            instant_book=csv_row.instant_book or False,
            
            bedrooms=csv_row.bedrooms,
            bathrooms=bathrooms,
            number_of_beds=number_of_beds,
            accommodates=csv_row.accommodates,
            person_capacity=person_capacity,
            
            price_tier=price_tier,
            revenue=revenue,
            revenue_potential=revenue_potential,
            adr=adr,
            cleaning_fee=cleaning_fee,
            
            property_reviews=csv_row.property_reviews,
            property_rating=csv_row.property_rating,
            stars=DataCleaner.clean_stars(csv_row.stars),
            
            data_quality_category=csv_row.data_quality_category,
            quality_rating_reason=csv_row.quality_rating_reason,
            
            superhost=superhost,
            is_guest_favorite=csv_row.is_guest_favorite or False,
            
            # Boolean amenities
            has_aircon=csv_row.has_aircon or False,
            has_gym=csv_row.has_gym or False,
            has_hottub=csv_row.has_hottub or False,
            has_kitchen=csv_row.has_kitchen or False,
            has_parking=csv_row.has_parking or False,
            has_pets_allowed=csv_row.has_pets_allowed or False,
            has_pool=csv_row.has_pool or False,
            
            system_gym=csv_row.system_gym or False,
            system_pool_table=csv_row.system_pool_table or False,
            system_arcade_machine=csv_row.system_arcade_machine or False,
            system_movie=csv_row.system_movie or False,
            system_bowling=csv_row.system_bowling or False,
            system_chess=csv_row.system_chess or False,
            system_golf=csv_row.system_golf or False,
            system_crib=csv_row.system_crib or False,
            system_pack_n_play=csv_row.system_pack_n_play or False,
            system_play_slide=csv_row.system_play_slide or False,
            system_firepit=csv_row.system_firepit or False,
            system_grill=csv_row.system_grill or False,
            system_pool=csv_row.system_pool or False,
            system_jacuzzi=csv_row.system_jacuzzi or False,
            system_view_ocean=csv_row.system_view_ocean or False,
            system_view_mountain=csv_row.system_view_mountain or False,
            
            has_outdoor_furniture=csv_row.has_outdoor_furniture or False,
            has_waterfront=csv_row.has_waterfront or False,
            has_lake_access=csv_row.has_lake_access or False,
            has_beach_access=csv_row.has_beach_access or False,
            has_outdoor_dining_area=csv_row.has_outdoor_dining_area or False,
            
            high_season_insights=csv_row.high_season_insights,
            
            amenities_list=amenities_list,
            
            # Review stats
            review_total_reviews=review_total,
            review_months_overall=review_months_overall,
            review_months_with_reviews=csv_row.review_months_with_reviews,
            review_months_without_reviews_overall=csv_row.review_months_without_reviews_overall,
            review_avg_reviews_per_month=review_avg_per_month,
            review_high_season_quarter=review_high_season_quarter,
            review_high_season_reviews=review_high_season_reviews,
            review_high_season_label=csv_row.review_high_season_label,
            review_count_stayed_with_kids=csv_row.review_count_stayed_with_kids,
            review_pct_stayed_with_kids=csv_row.review_pct_stayed_with_kids,
            review_count_group_trip=csv_row.review_count_group_trip,
            review_pct_group_trip=csv_row.review_pct_group_trip,
            review_count_stayed_with_a_pet=csv_row.review_count_stayed_with_a_pet,
            review_pct_stayed_with_a_pet=csv_row.review_pct_stayed_with_a_pet,
            review_missing_months_trailing_12=review_missing_trailing_12,
        )