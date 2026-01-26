from typing import Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from src.models.property import Property


def calculate_market_benchmarks(db: Session) -> Dict[str, Any]:
    """
    Calculate market benchmarks grouped by bedroom count.
    
    Returns dictionary with structure:
    {
        '1': {'avg_revenue': 50000, 'avg_adr': 150, 'adr_distribution': [...]},
        '2': {...},
        ...
    }
    """
    benchmarks = {}
    
    # Get all bedroom counts
    bedroom_counts = db.execute(
        select(Property.bedrooms)
        .where(Property.bedrooms.isnot(None))
        .distinct()
    ).scalars().all()
    
    for bedroom_count in bedroom_counts:
        # Get properties with this bedroom count
        properties = db.execute(
            select(Property)
            .where(Property.bedrooms == bedroom_count)
            .where(Property.revenue.isnot(None))
        ).scalars().all()
        
        if not properties:
            continue
        
        revenues = [float(p.revenue) for p in properties if p.revenue]
        adrs = [float(p.adr) for p in properties if p.adr]
        
        benchmarks[str(bedroom_count)] = {
            'avg_revenue': sum(revenues) / len(revenues) if revenues else 0,
            'median_revenue': _median(revenues) if revenues else 0,
            'top_25_pct': _percentile(revenues, 75) if revenues else 0,
            'avg_adr': sum(adrs) / len(adrs) if adrs else 0,
            'adr_distribution': adrs,
            'property_count': len(properties)
        }
    
    return benchmarks


def _median(values: list) -> float:
    """Calculate median of a list."""
    sorted_values = sorted(values)
    n = len(sorted_values)
    if n % 2 == 0:
        return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
    return sorted_values[n//2]


def _percentile(values: list, percentile: float) -> float:
    """Calculate percentile of a list."""
    sorted_values = sorted(values)
    index = int((percentile / 100) * len(sorted_values))
    return sorted_values[min(index, len(sorted_values) - 1)]