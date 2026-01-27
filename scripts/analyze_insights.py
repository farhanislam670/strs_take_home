#!/usr/bin/env python3
"""
Revenue Driver Analysis - Discover what factors drive STR revenue
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import func, case, and_
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.models.reviews import PropertyReview
import pandas as pd
from typing import Dict, List


def analyze_revenue_drivers():
    """Comprehensive analysis of what drives revenue"""
    
    db: Session = SessionLocal()
    
    print("=" * 80)
    print("STR REVENUE DRIVER ANALYSIS")
    print("=" * 80)
    print()
    
    # 1. AMENITY IMPACT ANALYSIS
    print("📊 1. AMENITY IMPACT ON REVENUE")
    print("-" * 80)
    amenity_impact = analyze_amenity_impact(db)
    print()
    
    # 2. BEDROOM COUNT ANALYSIS
    print("📊 2. BEDROOM COUNT PERFORMANCE")
    print("-" * 80)
    bedroom_analysis = analyze_bedroom_performance(db)
    print()
    
    # 3. MARKET COMPARISON
    print("📊 3. MARKET PERFORMANCE COMPARISON")
    print("-" * 80)
    market_analysis = analyze_market_performance(db)
    print()
    
    # 4. OCCUPANCY VS REVENUE
    print("📊 4. OCCUPANCY IMPACT ON REVENUE")
    print("-" * 80)
    occupancy_analysis = analyze_occupancy_impact(db)
    print()
    
    # 5. HOST STATUS IMPACT
    print("📊 5. HOST STATUS IMPACT")
    print("-" * 80)
    host_status_analysis = analyze_host_status(db)
    print()
    
    # 6. REVIEW IMPACT
    print("📊 6. REVIEW RATING IMPACT")
    print("-" * 80)
    review_analysis = analyze_review_impact(db)
    print()
    
    # 7. PRICE TIER ANALYSIS
    print("📊 7. PRICE TIER PERFORMANCE")
    print("-" * 80)
    price_tier_analysis = analyze_price_tiers(db)
    print()
    
    # 8. CORRELATION ANALYSIS
    print("📊 8. TOP REVENUE CORRELATIONS")
    print("-" * 80)
    correlation_analysis = analyze_correlations(db)
    print()
    
    # 9. KEY INSIGHTS SUMMARY
    print("=" * 80)
    print("🎯 KEY INSIGHTS SUMMARY")
    print("=" * 80)
    generate_key_insights(
        amenity_impact,
        bedroom_analysis,
        market_analysis,
        occupancy_analysis,
        host_status_analysis,
        review_analysis,
        price_tier_analysis,
        correlation_analysis
    )
    
    db.close()


def analyze_amenity_impact(db: Session) -> Dict:
    """Analyze which amenities drive the most revenue"""
    
    amenities_to_check = [
        ('has_pool', 'Pool'),
        ('has_hottub', 'Hot Tub'),
        ('has_waterfront', 'Waterfront'),
        ('has_beach_access', 'Beach Access'),
        ('system_view_ocean', 'Ocean View'),
        ('system_view_mountain', 'Mountain View'),
        ('has_gym', 'Gym'),
        ('system_firepit', 'Fire Pit'),
        ('system_grill', 'Grill'),
        ('has_lake_access', 'Lake Access'),
    ]
    
    results = []
    
    for field, name in amenities_to_check:
        # With amenity
        with_amenity = db.query(
            func.avg(Property.revenue).label('avg_revenue'),
            func.count(Property.property_id).label('count')
        ).filter(
            getattr(Property, field) == True,
            Property.revenue.isnot(None)
        ).first()
        
        # Without amenity
        without_amenity = db.query(
            func.avg(Property.revenue).label('avg_revenue'),
            func.count(Property.property_id).label('count')
        ).filter(
            getattr(Property, field) == False,
            Property.revenue.isnot(None)
        ).first()
        
        if with_amenity.avg_revenue and without_amenity.avg_revenue:
            impact = float(with_amenity.avg_revenue) - float(without_amenity.avg_revenue)
            impact_pct = (impact / float(without_amenity.avg_revenue)) * 100
            
            results.append({
                'amenity': name,
                'with_avg': float(with_amenity.avg_revenue),
                'without_avg': float(without_amenity.avg_revenue),
                'impact': impact,
                'impact_pct': impact_pct,
                'count_with': with_amenity.count,
                'count_without': without_amenity.count
            })
    
    # Sort by impact
    results.sort(key=lambda x: x['impact'], reverse=True)
    
    print(f"{'Amenity':<20} {'With':<12} {'Without':<12} {'Impact':<12} {'% Diff':<10} {'Count'}")
    print("-" * 80)
    
    for r in results[:10]:  # Top 10
        print(f"{r['amenity']:<20} ${r['with_avg']:>10,.0f} ${r['without_avg']:>10,.0f} "
              f"${r['impact']:>10,.0f} {r['impact_pct']:>8.1f}% {r['count_with']:>6}")
    
    return results


def analyze_bedroom_performance(db: Session) -> Dict:
    """Analyze revenue by bedroom count"""
    
    bedroom_stats = db.query(
        Property.bedrooms,
        func.count(Property.property_id).label('count'),
        func.avg(Property.revenue).label('avg_revenue'),
        func.avg(Property.occupancy).label('avg_occupancy'),
        func.avg(Property.adr).label('avg_adr')
    ).filter(
        Property.bedrooms.isnot(None),
        Property.revenue.isnot(None)
    ).group_by(
        Property.bedrooms
    ).order_by(
        Property.bedrooms
    ).all()
    
    print(f"{'Bedrooms':<12} {'Count':<8} {'Avg Revenue':<15} {'Avg Occupancy':<15} {'Avg ADR'}")
    print("-" * 80)
    
    results = []
    for stat in bedroom_stats:
        print(f"{stat.bedrooms:<12} {stat.count:<8} ${stat.avg_revenue:>12,.0f} "
              f"{stat.avg_occupancy:>13.1%} ${stat.avg_adr:>12,.0f}")
        results.append({
            'bedrooms': stat.bedrooms,
            'count': stat.count,
            'avg_revenue': float(stat.avg_revenue),
            'avg_occupancy': float(stat.avg_occupancy or 0),
            'avg_adr': float(stat.avg_adr or 0)
        })
    
    return results


def analyze_market_performance(db: Session) -> Dict:
    """Compare performance across markets"""
    
    market_stats = db.query(
        Property.market_area,
        func.count(Property.property_id).label('count'),
        func.avg(Property.revenue).label('avg_revenue'),
        func.avg(Property.occupancy).label('avg_occupancy'),
        func.avg(Property.adr).label('avg_adr'),
        func.avg(InvestmentScore.total_score).label('avg_score')
    ).join(
        InvestmentScore,
        Property.property_id == InvestmentScore.property_id
    ).filter(
        Property.revenue.isnot(None)
    ).group_by(
        Property.market_area
    ).order_by(
        func.avg(Property.revenue).desc()
    ).all()
    
    print(f"{'Market':<20} {'Count':<8} {'Avg Revenue':<15} {'Occupancy':<12} {'ADR':<12} {'Score'}")
    print("-" * 80)
    
    results = []
    for stat in market_stats:
        print(f"{stat.market_area:<20} {stat.count:<8} ${stat.avg_revenue:>12,.0f} "
              f"{stat.avg_occupancy:>10.1%} ${stat.avg_adr:>10,.0f} {stat.avg_score:>6.1f}")
        results.append({
            'market': stat.market_area,
            'count': stat.count,
            'avg_revenue': float(stat.avg_revenue),
            'avg_occupancy': float(stat.avg_occupancy or 0),
            'avg_adr': float(stat.avg_adr or 0),
            'avg_score': float(stat.avg_score or 0)
        })
    
    return results


def analyze_occupancy_impact(db: Session) -> Dict:
    """Analyze revenue by occupancy tiers"""
    
    occupancy_tiers = db.query(
        case(
            (Property.occupancy < 0.5, 'Low (<50%)'),
            (Property.occupancy < 0.7, 'Medium (50-70%)'),
            (Property.occupancy < 0.85, 'High (70-85%)'),
            else_='Very High (85%+)'
        ).label('tier'),
        func.count(Property.property_id).label('count'),
        func.avg(Property.revenue).label('avg_revenue'),
        func.avg(Property.adr).label('avg_adr')
    ).filter(
        Property.occupancy.isnot(None),
        Property.revenue.isnot(None)
    ).group_by('tier').all()
    
    print(f"{'Occupancy Tier':<20} {'Count':<8} {'Avg Revenue':<15} {'Avg ADR'}")
    print("-" * 80)
    
    results = []
    for tier in occupancy_tiers:
        print(f"{tier.tier:<20} {tier.count:<8} ${tier.avg_revenue:>12,.0f} ${tier.avg_adr:>12,.0f}")
        results.append({
            'tier': tier.tier,
            'count': tier.count,
            'avg_revenue': float(tier.avg_revenue),
            'avg_adr': float(tier.avg_adr or 0)
        })
    
    return results


def analyze_host_status(db: Session) -> Dict:
    """Analyze impact of host status on revenue"""
    
    # Superhost impact
    superhost_yes = db.query(
        func.avg(Property.revenue).label('avg_revenue'),
        func.count(Property.property_id).label('count')
    ).filter(
        Property.superhost == True,
        Property.revenue.isnot(None)
    ).first()
    
    superhost_no = db.query(
        func.avg(Property.revenue).label('avg_revenue'),
        func.count(Property.property_id).label('count')
    ).filter(
        Property.superhost == False,
        Property.revenue.isnot(None)
    ).first()
    
    # Guest favorite impact
    favorite_yes = db.query(
        func.avg(Property.revenue).label('avg_revenue'),
        func.count(Property.property_id).label('count')
    ).filter(
        Property.is_guest_favorite == True,
        Property.revenue.isnot(None)
    ).first()
    
    favorite_no = db.query(
        func.avg(Property.revenue).label('avg_revenue'),
        func.count(Property.property_id).label('count')
    ).filter(
        Property.is_guest_favorite == False,
        Property.revenue.isnot(None)
    ).first()
    
    superhost_impact = float(superhost_yes.avg_revenue) - float(superhost_no.avg_revenue)
    superhost_pct = (superhost_impact / float(superhost_no.avg_revenue)) * 100
    
    favorite_impact = float(favorite_yes.avg_revenue) - float(favorite_no.avg_revenue)
    favorite_pct = (favorite_impact / float(favorite_no.avg_revenue)) * 100
    
    print(f"{'Status':<25} {'With':<15} {'Without':<15} {'Impact':<15} {'% Diff'}")
    print("-" * 80)
    print(f"{'Superhost':<25} ${superhost_yes.avg_revenue:>12,.0f} "
          f"${superhost_no.avg_revenue:>12,.0f} ${superhost_impact:>12,.0f} {superhost_pct:>8.1f}%")
    print(f"{'Guest Favorite':<25} ${favorite_yes.avg_revenue:>12,.0f} "
          f"${favorite_no.avg_revenue:>12,.0f} ${favorite_impact:>12,.0f} {favorite_pct:>8.1f}%")
    
    return {
        'superhost': {
            'with': float(superhost_yes.avg_revenue),
            'without': float(superhost_no.avg_revenue),
            'impact': superhost_impact,
            'impact_pct': superhost_pct
        },
        'guest_favorite': {
            'with': float(favorite_yes.avg_revenue),
            'without': float(favorite_no.avg_revenue),
            'impact': favorite_impact,
            'impact_pct': favorite_pct
        }
    }


def analyze_review_impact(db: Session) -> Dict:
    """Analyze impact of reviews on revenue"""
    
    rating_tiers = db.query(
        case(
            (Property.stars < 4.0, 'Low (<4.0)'),
            (Property.stars < 4.5, 'Good (4.0-4.5)'),
            (Property.stars < 4.8, 'Great (4.5-4.8)'),
            else_='Excellent (4.8+)'
        ).label('tier'),
        func.count(Property.property_id).label('count'),
        func.avg(Property.revenue).label('avg_revenue'),
        func.avg(Property.occupancy).label('avg_occupancy')
    ).filter(
        Property.stars.isnot(None),
        Property.revenue.isnot(None)
    ).group_by('tier').all()
    
    print(f"{'Rating Tier':<20} {'Count':<8} {'Avg Revenue':<15} {'Avg Occupancy'}")
    print("-" * 80)
    
    results = []
    for tier in rating_tiers:
        print(f"{tier.tier:<20} {tier.count:<8} ${tier.avg_revenue:>12,.0f} {tier.avg_occupancy:>13.1%}")
        results.append({
            'tier': tier.tier,
            'count': tier.count,
            'avg_revenue': float(tier.avg_revenue),
            'avg_occupancy': float(tier.avg_occupancy or 0)
        })
    
    return results


def analyze_price_tiers(db: Session) -> Dict:
    """Analyze performance by price tier"""
    
    tier_stats = db.query(
        Property.price_tier,
        func.count(Property.property_id).label('count'),
        func.avg(Property.revenue).label('avg_revenue'),
        func.avg(Property.occupancy).label('avg_occupancy'),
        func.avg(Property.adr).label('avg_adr')
    ).filter(
        Property.price_tier.isnot(None),
        Property.revenue.isnot(None)
    ).group_by(
        Property.price_tier
    ).order_by(
        func.avg(Property.revenue).desc()
    ).all()
    
    print(f"{'Price Tier':<20} {'Count':<8} {'Avg Revenue':<15} {'Occupancy':<12} {'ADR'}")
    print("-" * 80)
    
    results = []
    for stat in tier_stats:
        print(f"{stat.price_tier:<20} {stat.count:<8} ${stat.avg_revenue:>12,.0f} "
              f"{stat.avg_occupancy:>10.1%} ${stat.avg_adr:>10,.0f}")
        results.append({
            'tier': stat.price_tier,
            'count': stat.count,
            'avg_revenue': float(stat.avg_revenue),
            'avg_occupancy': float(stat.avg_occupancy or 0),
            'avg_adr': float(stat.avg_adr or 0)
        })
    
    return results


def analyze_correlations(db: Session) -> Dict:
    """Analyze correlations between various factors and revenue"""
    
    # Get all data for correlation analysis
    properties = db.query(
        Property.revenue,
        Property.occupancy,
        Property.adr,
        Property.bedrooms,
        Property.bathrooms,
        Property.property_reviews,
        Property.stars,
        Property.has_pool,
        Property.has_hottub,
        Property.has_waterfront,
        Property.superhost,
        Property.is_guest_favorite
    ).filter(
        Property.revenue.isnot(None)
    ).all()
    
    # Convert to DataFrame for correlation analysis
    df = pd.DataFrame([{
        'revenue': float(p.revenue),
        'occupancy': float(p.occupancy or 0),
        'adr': float(p.adr or 0),
        'bedrooms': int(p.bedrooms or 0),
        'bathrooms': float(p.bathrooms or 0),
        'reviews': int(p.property_reviews or 0),
        'stars': float(p.stars or 0),
        'has_pool': int(p.has_pool),
        'has_hottub': int(p.has_hottub),
        'has_waterfront': int(p.has_waterfront),
        'superhost': int(p.superhost),
        'guest_favorite': int(p.is_guest_favorite)
    } for p in properties])
    
    # Calculate correlations with revenue
    correlations = df.corr()['revenue'].sort_values(ascending=False)
    
    print(f"{'Factor':<20} {'Correlation with Revenue':<25}")
    print("-" * 80)
    for factor, corr in correlations.items():
        if factor != 'revenue':
            print(f"{factor:<20} {corr:>24.3f}")
    
    return correlations.to_dict()


def generate_key_insights(amenity_impact, bedroom_analysis, market_analysis, 
                         occupancy_analysis, host_status_analysis, review_analysis,
                         price_tier_analysis, correlation_analysis):
    """Generate human-readable key insights"""
    
    # Top revenue-driving amenity
    top_amenity = amenity_impact[0]
    print(f"🏆 Top Revenue Driver (Amenity): {top_amenity['amenity']}")
    print(f"   Impact: +${top_amenity['impact']:,.0f} ({top_amenity['impact_pct']:.1f}% increase)")
    print()
    
    # Best performing bedroom count
    best_bedroom = max(bedroom_analysis, key=lambda x: x['avg_revenue'])
    print(f"🏠 Best Performing Bedroom Count: {best_bedroom['bedrooms']} bedrooms")
    print(f"   Avg Revenue: ${best_bedroom['avg_revenue']:,.0f}")
    print()
    
    # Best market
    best_market = market_analysis[0]
    print(f"📍 Highest Revenue Market: {best_market['market']}")
    print(f"   Avg Revenue: ${best_market['avg_revenue']:,.0f}")
    print(f"   Avg Occupancy: {best_market['avg_occupancy']:.1%}")
    print()
    
    # Superhost impact
    print(f"⭐ Superhost Impact: +${host_status_analysis['superhost']['impact']:,.0f} "
          f"({host_status_analysis['superhost']['impact_pct']:.1f}% boost)")
    print()
    
    # Top 3 correlations
    print("📈 Strongest Revenue Correlations:")
    top_3_corr = sorted(correlation_analysis.items(), key=lambda x: x[1], reverse=True)[1:4]
    for i, (factor, corr) in enumerate(top_3_corr, 1):
        print(f"   {i}. {factor}: {corr:.3f}")
    print()
    
    print("💡 ACTIONABLE INSIGHTS:")
    print("   • Invest in properties with", top_amenity['amenity'].lower())
    print("   • Target", best_bedroom['bedrooms'], "bedroom properties")
    print("   • Focus on", best_market['market'], "market")
    print("   • Prioritize Superhost status for revenue boost")
    print("   • Maintain high ratings (4.8+) for maximum revenue")


if __name__ == "__main__":
    analyze_revenue_drivers()