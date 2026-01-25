from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from src.models.property import Property
from src.models.amenities import PropertyAmenity
from src.models.reviews import PropertyReview
from src.schemas.property_csv import CleanedPropertyData
from typing import List
import logging

logger = logging.getLogger(__name__)


class DatabaseWriter:
    """Writes cleaned data to database."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def upsert_properties(self, properties: List[CleanedPropertyData]) -> int:
        """
        Upsert properties using PostgreSQL's ON CONFLICT.
        
        Returns:
            Number of properties upserted
        """
        if not properties:
            return 0
        
        logger.info(f"Upserting {len(properties)} properties...")
        
        property_records = []
        amenity_records = []
        review_records = []
        
        for prop_data in properties:
            # Prepare property record
            property_dict = {
                'property_id': prop_data.property_id,
                'property_manager_host_id': prop_data.property_manager_host_id,
                'title': prop_data.title,
                'market_area': prop_data.market_area,
                'property_type': prop_data.property_type,
                'description': prop_data.description,
                'city_name': prop_data.city_name,
                'state_name': prop_data.state_name,
                'zipcode': prop_data.zipcode,
                'latitude': prop_data.latitude,
                'longitude': prop_data.longitude,
                'airbnb_host_url': prop_data.airbnb_host_url,
                'airbnb_listing_url': prop_data.airbnb_listing_url,
                'vrbo_listing_url': prop_data.vrbo_listing_url,
                'minimum_stay': prop_data.minimum_stay,
                'available_nights': prop_data.available_nights,
                'occupancy': prop_data.occupancy,
                'instant_book': prop_data.instant_book,
                'bedrooms': prop_data.bedrooms,
                'bathrooms': prop_data.bathrooms,
                'number_of_beds': prop_data.number_of_beds,
                'accommodates': prop_data.accommodates,
                'person_capacity': prop_data.person_capacity,
                'price_tier': prop_data.price_tier,
                'revenue': prop_data.revenue,
                'revenue_potential': prop_data.revenue_potential,
                'adr': prop_data.adr,
                'cleaning_fee': prop_data.cleaning_fee,
                'property_reviews': prop_data.property_reviews,
                'property_rating': prop_data.property_rating,
                'stars': prop_data.stars,
                'data_quality_category': prop_data.data_quality_category,
                'quality_rating_reason': prop_data.quality_rating_reason,
                'superhost': prop_data.superhost,
                'is_guest_favorite': prop_data.is_guest_favorite,
                'has_aircon': prop_data.has_aircon,
                'has_gym': prop_data.has_gym,
                'has_hottub': prop_data.has_hottub,
                'has_kitchen': prop_data.has_kitchen,
                'has_parking': prop_data.has_parking,
                'has_pets_allowed': prop_data.has_pets_allowed,
                'has_pool': prop_data.has_pool,
                'system_gym': prop_data.system_gym,
                'system_pool_table': prop_data.system_pool_table,
                'system_arcade_machine': prop_data.system_arcade_machine,
                'system_movie': prop_data.system_movie,
                'system_bowling': prop_data.system_bowling,
                'system_chess': prop_data.system_chess,
                'system_golf': prop_data.system_golf,
                'system_crib': prop_data.system_crib,
                'system_pack_n_play': prop_data.system_pack_n_play,
                'system_play_slide': prop_data.system_play_slide,
                'system_firepit': prop_data.system_firepit,
                'system_grill': prop_data.system_grill,
                'system_pool': prop_data.system_pool,
                'system_jacuzzi': prop_data.system_jacuzzi,
                'system_view_ocean': prop_data.system_view_ocean,
                'system_view_mountain': prop_data.system_view_mountain,
                'has_outdoor_furniture': prop_data.has_outdoor_furniture,
                'has_waterfront': prop_data.has_waterfront,
                'has_lake_access': prop_data.has_lake_access,
                'has_beach_access': prop_data.has_beach_access,
                'has_outdoor_dining_area': prop_data.has_outdoor_dining_area,
                'high_season_insights': prop_data.high_season_insights,
            }
            property_records.append(property_dict)
            
            # Prepare amenity record
            amenity_dict = {
                'property_id': prop_data.property_id,
                'amenities': prop_data.amenities_list,
            }
            amenity_records.append(amenity_dict)
            
            # Prepare review record
            review_dict = {
                'property_id': prop_data.property_id,
                'review_total_reviews': prop_data.review_total_reviews,
                'review_months_overall': prop_data.review_months_overall,
                'review_months_with_reviews': prop_data.review_months_with_reviews,
                'review_months_without_reviews_overall': prop_data.review_months_without_reviews_overall,
                'review_avg_reviews_per_month': prop_data.review_avg_reviews_per_month,
                'review_high_season_quarter': prop_data.review_high_season_quarter,
                'review_high_season_reviews': prop_data.review_high_season_reviews,
                'review_high_season_label': prop_data.review_high_season_label,
                'review_count_stayed_with_kids': prop_data.review_count_stayed_with_kids,
                'review_pct_stayed_with_kids': prop_data.review_pct_stayed_with_kids,
                'review_count_group_trip': prop_data.review_count_group_trip,
                'review_pct_group_trip': prop_data.review_pct_group_trip,
                'review_count_stayed_with_a_pet': prop_data.review_count_stayed_with_a_pet,
                'review_pct_stayed_with_a_pet': prop_data.review_pct_stayed_with_a_pet,
                'review_missing_months_trailing_12': prop_data.review_missing_months_trailing_12,
            }
            review_records.append(review_dict)
        
        # Get a sample dict for column names (use first record)
        sample_property_dict = property_records[0]
        sample_amenity_dict = amenity_records[0]
        sample_review_dict = review_records[0]
        
        # Batch upsert properties - THIS IS THE FIX!
        stmt = insert(Property).values(property_records)  # Pass the WHOLE list
        stmt = stmt.on_conflict_do_update(
            index_elements=['property_id'],
            set_={k: stmt.excluded[k] for k in sample_property_dict.keys() if k != 'property_id'}
        )
        self.session.execute(stmt)
        logger.info(f"Upserted {len(property_records)} properties")
        
        # Batch upsert amenities
        stmt = insert(PropertyAmenity).values(amenity_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['property_id'],
            set_={k: stmt.excluded[k] for k in sample_amenity_dict.keys() if k != 'property_id'}
        )
        self.session.execute(stmt)
        logger.info(f"Upserted {len(amenity_records)} amenity records")
        
        # Batch upsert reviews
        stmt = insert(PropertyReview).values(review_records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['property_id'],
            set_={k: stmt.excluded[k] for k in sample_review_dict.keys() if k != 'property_id'}
        )
        self.session.execute(stmt)
        logger.info(f"Upserted {len(review_records)} review records")
        
        self.session.commit()
        
        return len(property_records)