from typing import Dict, Any, Optional
from src.models.property import Property
from src.models.reviews import PropertyReview


def calculate_revenue_score(
    property: Property,
    market_benchmarks: Dict[str, Any]
) -> Dict[str, float]:
    """
    Calculate revenue performance score.
    Returns score and supporting metrics.
    """
    if not property.revenue or not property.bedrooms:
        return {'score': 0, 'revenue_ratio': 0, 'potential_gap': 0}
    
    bedroom_key = str(property.bedrooms)
    if bedroom_key not in market_benchmarks:
        return {'score': 50, 'revenue_ratio': 1.0, 'potential_gap': 0}
    
    market_avg = market_benchmarks[bedroom_key]['avg_revenue']
    
    if market_avg == 0:
        return {'score': 50, 'revenue_ratio': 1.0, 'potential_gap': 0}
    
    # Revenue vs Market Average
    revenue_ratio = float(property.revenue) / market_avg
    
    # Revenue Potential Gap
    if property.revenue_potential and property.revenue:
        potential_gap = (float(property.revenue_potential) - float(property.revenue)) / float(property.revenue)
    else:
        potential_gap = 0
    
    # Base score
    base_score = min(100, revenue_ratio * 100)
    
    # Bonus for exceeding market
    if revenue_ratio > 1:
        base_score += (revenue_ratio - 1) * 50
    
    # Bonus for high potential gap (opportunity)
    if potential_gap > 0.2:
        base_score += 20
    
    score = min(100, base_score)
    
    return {
        'score': score,
        'revenue_ratio': revenue_ratio,
        'potential_gap': potential_gap
    }


def calculate_occupancy_score(
    property: Property,
    review_stats: Optional[PropertyReview]
) -> float:
    """Calculate occupancy quality and consistency score."""
    if not review_stats:
        # Fallback to basic occupancy
        return (property.occupancy or 0) * 100
    
    occupancy = property.occupancy or 0
    occupancy_score = occupancy * 100
    
    # Consistency bonus
    months_with_reviews = review_stats.review_months_with_reviews or 0
    total_months = review_stats.review_months_overall or 0
    
    if total_months > 0:
        consistency = months_with_reviews / total_months
        consistency_bonus = consistency * 20
    else:
        consistency_bonus = 0
    
    # Penalty for recent gaps
    missing_months = review_stats.review_missing_months_trailing_12 or 0
    if missing_months > 3:
        gap_penalty = missing_months * 5
    else:
        gap_penalty = 0
    
    total = occupancy_score + consistency_bonus - gap_penalty
    return max(0, min(100, total))


def calculate_market_positioning_score(
    property: Property,
    market_benchmarks: Dict[str, Any]
) -> float:
    """Calculate ADR and price tier positioning score."""
    if not property.bedrooms:
        return 50
    
    bedroom_key = str(property.bedrooms)
    if bedroom_key not in market_benchmarks:
        return 50
    
    market_data = market_benchmarks[bedroom_key]
    
    # ADR Percentile
    if property.adr and 'adr_distribution' in market_data:
        adr_percentile = _calculate_percentile(
            float(property.adr),
            market_data['adr_distribution']
        )
        
        # Sweet spot: 60-85th percentile
        if 60 <= adr_percentile <= 85:
            adr_score = 100
        elif adr_percentile > 85:
            adr_score = 70
        else:
            adr_score = adr_percentile
    else:
        adr_score = 50
    
    # Price tier score
    tier_scores = {
        'Luxury': 85,
        'Upper Upscale': 90,
        'Upscale': 100,
        'Upper Midscale': 80,
        'Midscale': 60,
        'Economy': 40
    }
    tier_score = tier_scores.get(property.price_tier, 50)
    
    return (adr_score * 0.6) + (tier_score * 0.4)


def calculate_review_score(
    property: Property,
    review_stats: Optional[PropertyReview]
) -> float:
    """Calculate review strength score."""
    if not review_stats:
        # Basic fallback
        rating = property.property_rating or 0
        stars = property.stars or 0
        return (stars / 5) * 100 if stars else (rating / 5) * 100
    
    # Volume score
    total_reviews = property.property_reviews or 0
    volume_score = min(100, (total_reviews / 50) * 100)
    
    # Rating score
    stars = property.stars or 0
    rating_score = (stars / 5) * 100
    
    # Velocity score
    avg_per_month = review_stats.review_avg_reviews_per_month or 0
    velocity_score = min(100, avg_per_month * 20)
    
    # Recency bonus
    high_season_reviews = review_stats.review_high_season_reviews or 0
    if high_season_reviews > 10:
        recency_bonus = 15
    elif high_season_reviews > 5:
        recency_bonus = 10
    else:
        recency_bonus = 0
    
    total = (
        volume_score * 0.3 +
        rating_score * 0.4 +
        velocity_score * 0.3 +
        recency_bonus
    )
    
    return min(100, total)


def calculate_amenity_score(
    property: Property,
    review_stats: Optional[PropertyReview]
) -> float:
    """Calculate amenity value score."""
    score = 0
    
    # High-value amenities (15 points each)
    high_value_amenities = [
        property.has_pool or property.system_pool,
        property.has_hottub or property.system_jacuzzi,
        property.has_waterfront,
        property.has_beach_access,
        property.system_view_ocean,
        property.system_view_mountain,
        property.system_firepit,
        property.system_grill
    ]
    score += sum(high_value_amenities) * 15
    
    # Medium-value amenities (8 points each)
    medium_value_amenities = [
        property.has_gym or property.system_gym,
        property.system_pool_table or property.system_arcade_machine,
        property.has_lake_access,
        property.has_outdoor_dining_area
    ]
    score += sum(medium_value_amenities) * 8
    
    # Family amenities (conditional bonus)
    if review_stats and review_stats.review_pct_stayed_with_kids:
        if review_stats.review_pct_stayed_with_kids > 0.3:
            family_amenities = [
                property.system_crib,
                property.system_pack_n_play,
                property.system_play_slide
            ]
            score += sum(family_amenities) * 10
    
    # Basic amenities (5 points each)
    basic_amenities = [
        property.has_aircon,
        property.has_kitchen,
        property.has_parking,
        property.has_pets_allowed
    ]
    score += sum(basic_amenities) * 5
    
    return min(100, score)


def calculate_host_status_score(property: Property) -> float:
    """Calculate host status score."""
    score = 0
    
    if property.superhost:
        score += 60
    
    if property.is_guest_favorite:
        score += 40
    
    if property.instant_book:
        score += 20
    
    return min(100, score)


def calculate_seasonal_stability_score(
    property: Property,
    review_stats: Optional[PropertyReview]
) -> float:
    """Calculate seasonal stability score."""
    if not review_stats:
        return 50  # Neutral score
    
    high_season_reviews = review_stats.review_high_season_reviews or 0
    total_reviews = review_stats.review_total_reviews or 1
    
    # Calculate concentration
    high_season_concentration = high_season_reviews / total_reviews
    
    # Sweet spot: 40-60% in high season
    if 0.4 <= high_season_concentration <= 0.6:
        stability_score = 100
    elif high_season_concentration > 0.8:
        stability_score = 40  # Too seasonal
    else:
        stability_score = 70
    
    # Bonus for year-round activity
    missing_months = review_stats.review_missing_months_trailing_12 or 0
    if missing_months == 0:
        stability_score = min(100, stability_score + 20)
    
    return stability_score


def _calculate_percentile(value: float, distribution: list) -> float:
    """Helper to calculate percentile of a value in a distribution."""
    if not distribution:
        return 50
    
    sorted_dist = sorted(distribution)
    count_below = sum(1 for x in sorted_dist if x < value)
    
    percentile = (count_below / len(sorted_dist)) * 100
    return percentile