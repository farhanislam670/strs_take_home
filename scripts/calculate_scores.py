#!/usr/bin/env python3
"""
Script to calculate and update investment scores for all properties.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session, joinedload
from src.database import SessionLocal
from src.models.property import Property
from src.models.investment_score import InvestmentScore
from src.scoring.calculator import calculate_investment_score
from src.scoring.benchmarks import calculate_market_benchmarks


def update_investment_scores(batch_size: int = 100):
    """Calculate and store investment scores for all properties."""
    db: Session = SessionLocal()
    
    try:
        print("📊 Calculating market benchmarks...")
        market_benchmarks = calculate_market_benchmarks(db)
        print(f"✓ Benchmarks calculated for {len(market_benchmarks)} bedroom configurations")
        
        # Get total count
        total_properties = db.query(Property).count()
        print(f"\n🏠 Processing {total_properties} properties...")
        
        # Process in batches
        processed = 0
        updated = 0
        created = 0
        errors = 0
        
        offset = 0
        while True:
            # Fetch batch with relationships
            properties = db.query(Property).options(
                joinedload(Property.review_stats)
            ).limit(batch_size).offset(offset).all()
            
            if not properties:
                break
            
            for property in properties:
                try:
                    # Calculate score
                    score_data = calculate_investment_score(property, market_benchmarks)
                    
                    # Check if score exists
                    existing_score = db.query(InvestmentScore).filter(
                        InvestmentScore.property_id == property.property_id
                    ).first()
                    
                    if existing_score:
                        # Update existing
                        for key, value in score_data.items():
                            if key == 'breakdown':
                                existing_score.revenue_score = value['revenue']
                                existing_score.occupancy_score = value['occupancy']
                                existing_score.positioning_score = value['positioning']
                                existing_score.review_score = value['reviews']
                                existing_score.amenity_score = value['amenities']
                                existing_score.host_status_score = value['host_status']
                                existing_score.seasonal_score = value['seasonal']
                            elif hasattr(existing_score, key):
                                setattr(existing_score, key, value)
                        updated += 1
                    else:
                        # Create new
                        new_score = InvestmentScore(
                            property_id=property.property_id,
                            total_score=score_data['total_score'],
                            grade=score_data['grade'],
                            investment_tier=score_data['investment_tier'],
                            revenue_score=score_data['breakdown']['revenue'],
                            occupancy_score=score_data['breakdown']['occupancy'],
                            positioning_score=score_data['breakdown']['positioning'],
                            review_score=score_data['breakdown']['reviews'],
                            amenity_score=score_data['breakdown']['amenities'],
                            host_status_score=score_data['breakdown']['host_status'],
                            seasonal_score=score_data['breakdown']['seasonal'],
                            market_area=score_data['market_area'],
                            bedroom_count=score_data['bedroom_count'],
                            revenue_vs_market_avg=score_data['revenue_vs_market_avg'],
                            revenue_potential_gap=score_data['revenue_potential_gap'],
                            is_top_opportunity=score_data['is_top_opportunity'],
                            score_breakdown=score_data['score_breakdown']
                        )
                        db.add(new_score)
                        created += 1
                    
                    processed += 1
                    
                    # Progress indicator
                    if processed % 10 == 0:
                        print(f"  Processed {processed}/{total_properties}", end='\r')
                
                except Exception as e:
                    print(f"\n❌ Error processing {property.property_id}: {e}")
                    errors += 1
                    continue
            
            # Commit batch
            db.commit()
            offset += batch_size
        
        print(f"\n\n✅ Complete!")
        print(f"  • Processed: {processed}")
        print(f"  • Created: {created}")
        print(f"  • Updated: {updated}")
        print(f"  • Errors: {errors}")
        
        # Show top opportunities
        print("\n🌟 Top Investment Opportunities:")
        top_scores = db.query(InvestmentScore).filter(
            InvestmentScore.is_top_opportunity == True
        ).order_by(InvestmentScore.total_score.desc()).limit(10).all()
        
        for i, score in enumerate(top_scores, 1):
            print(f"  {i}. {score.property_id} - Score: {score.total_score} ({score.grade}) - {score.market_area}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_investment_scores()