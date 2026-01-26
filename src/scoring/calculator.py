from typing import Dict, Any, Optional
from src.models.property import Property
from src.models.reviews import PropertyReview
from src.scoring.factors import (
    calculate_revenue_score,
    calculate_occupancy_score,
    calculate_market_positioning_score,
    calculate_review_score,
    calculate_amenity_score,
    calculate_host_status_score,
    calculate_seasonal_stability_score
)


# Configurable weights
SCORE_WEIGHTS = {
    'revenue_performance': 0.25,
    'occupancy_quality': 0.20,
    'market_positioning': 0.15,
    'review_strength': 0.15,
    'amenity_value': 0.10,
    'host_status': 0.05,
    'seasonal_stability': 0.10,
}


def calculate_investment_score(
    property: Property,
    market_benchmarks: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate comprehensive investment score for a property.
    
    Args:
        property: Property model instance
        market_benchmarks: Market data for comparison
        
    Returns:
        Dictionary with total score, breakdown, and metrics
    """
    review_stats = property.review_stats if hasattr(property, 'review_stats') else None
    
    # Calculate individual scores
    revenue_data = calculate_revenue_score(property, market_benchmarks)
    
    scores = {
        'revenue': revenue_data['score'],
        'occupancy': calculate_occupancy_score(property, review_stats),
        'positioning': calculate_market_positioning_score(property, market_benchmarks),
        'reviews': calculate_review_score(property, review_stats),
        'amenities': calculate_amenity_score(property, review_stats),
        'host_status': calculate_host_status_score(property),
        'seasonal': calculate_seasonal_stability_score(property, review_stats)
    }
    
    # Calculate weighted total
    total_score = (
        scores['revenue'] * SCORE_WEIGHTS['revenue_performance'] +
        scores['occupancy'] * SCORE_WEIGHTS['occupancy_quality'] +
        scores['positioning'] * SCORE_WEIGHTS['market_positioning'] +
        scores['reviews'] * SCORE_WEIGHTS['review_strength'] +
        scores['amenities'] * SCORE_WEIGHTS['amenity_value'] +
        scores['host_status'] * SCORE_WEIGHTS['host_status'] +
        scores['seasonal'] * SCORE_WEIGHTS['seasonal_stability']
    )
    
    grade = _assign_grade(total_score)
    tier = _assign_tier(total_score)
    is_top = total_score >= 85
    
    return {
        'total_score': round(total_score, 2),
        'grade': grade,
        'investment_tier': tier,
        'is_top_opportunity': is_top,
        'breakdown': scores,
        'revenue_vs_market_avg': revenue_data['revenue_ratio'],
        'revenue_potential_gap': revenue_data['potential_gap'],
        'market_area': property.market_area,
        'bedroom_count': property.bedrooms,
        'score_breakdown': {
            'component_scores': scores,
            'weights': SCORE_WEIGHTS,
            'revenue_metrics': {
                'revenue_ratio': revenue_data['revenue_ratio'],
                'potential_gap': revenue_data['potential_gap']
            }
        }
    }


def _assign_grade(score: float) -> str:
    """Assign letter grade based on score."""
    if score >= 90: return 'A+'
    if score >= 85: return 'A'
    if score >= 80: return 'A-'
    if score >= 75: return 'B+'
    if score >= 70: return 'B'
    if score >= 65: return 'B-'
    if score >= 60: return 'C+'
    if score >= 55: return 'C'
    if score >= 50: return 'C-'
    return 'D'


def _assign_tier(score: float) -> str:
    """Assign investment tier based on score."""
    if score >= 85: return 'PRIME'
    if score >= 75: return 'STRONG'
    if score >= 65: return 'MODERATE'
    if score >= 50: return 'ACCEPTABLE'
    return 'UNDERPERFORMING'