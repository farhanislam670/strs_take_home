# Property Investment Scoring Algorithm

## Overview
This algorithm evaluates short-term rental properties (e.g., Airbnb) using a weighted composite score (0-100) that identifies high-performing investment opportunities. Properties are ranked by combining seven key performance factors, each normalized to a 0-100 scale.

## Scoring Components & Weights

### 1. Revenue Performance (25%)
**Purpose:** Measure earning power relative to market and potential

**Calculation:**
- Base score: (Property Revenue / Market Average Revenue) × 100
- Bonus: +50% for each point above market average
- Opportunity bonus: +20 points if revenue potential gap > 20%
- Cap: 100 points max

**Why it matters:** Revenue is the primary indicator of investment returns. Properties exceeding market averages demonstrate competitive advantage.

### 2. Occupancy Quality (20%)
**Purpose:** Assess booking consistency and stability

**Calculation:**
- Base: Current occupancy rate × 100
- Consistency bonus: (Months with reviews / Total months) × 20
- Gap penalty: -5 points per missing month (if > 3 months)

**Why it matters:** High, consistent occupancy indicates reliable cash flow and market demand.

### 3. Market Positioning (15%)
**Purpose:** Evaluate pricing strategy and competitive positioning

**Calculation:**
- ADR percentile score (60-85th percentile = optimal, 100 points)
- Price tier multiplier: Upscale (100) > Upper Upscale (90) > Luxury (85) > Upper Midscale (80) > Midscale (60) > Economy (40)
- Weighted: ADR score × 0.6 + Tier score × 0.4

**Why it matters:** Properties in the "sweet spot" (premium but not luxury) maximize revenue without limiting demand.

### 4. Review Strength (15%)
**Purpose:** Measure guest satisfaction and marketing strength

**Calculation:**
- Volume: min(100, (Total Reviews / 50) × 100) × 0.3
- Rating: (Stars / 5) × 100 × 0.4
- Velocity: min(100, Avg Reviews per Month × 20) × 0.3
- Recency bonus: +10-15 points for high-season activity

**Why it matters:** Strong reviews drive bookings through platform algorithms and social proof.

### 5. Amenity Value (10%)
**Purpose:** Quantify property features that command premium rates

**Calculation:**
- High-value amenities: 15 points each (pool, hot tub, waterfront, ocean view, mountain view)
- Medium-value amenities: 8 points each (gym, game room, lake access)
- Family amenities: 10 points each if >30% family guests (crib, play equipment)
- Basic amenities: 5 points each (AC, kitchen, parking, pet-friendly)

**Why it matters:** Premium amenities justify higher ADR and attract specific high-value guest segments.

### 6. Host Status (5%)
**Purpose:** Account for platform recognition and booking advantages

**Calculation:**
- Superhost: +60 points
- Guest Favorite: +40 points
- Instant Book: +20 points
- Cap: 100 points

**Why it matters:** Platform badges increase visibility and conversion rates.

### 7. Seasonal Stability (10%)
**Purpose:** Identify year-round performers vs. seasonal properties

**Calculation:**
- Optimal concentration: 40-60% high-season reviews = 100 points
- Over-concentrated (>80% high season): 40 points (risk flag)
- Year-round bonus: +20 points if no missing months

**Why it matters:** Year-round performance reduces cash flow volatility and risk.

## Final Score Calculation

**Total Score = Σ(Component Score × Weight)**

Example:
```
Revenue (85 × 0.25) + Occupancy (78 × 0.20) + Positioning (92 × 0.15) + 
Reviews (88 × 0.15) + Amenities (75 × 0.10) + Host (60 × 0.05) + 
Seasonal (90 × 0.10) = 82.45
```

## Grading & Classification

**Letter Grades:**
- A+ (90-100): Exceptional performers
- A (85-89): Top-tier opportunities
- A- to B+ (75-84): Strong performers
- B to C (50-74): Acceptable to moderate
- D (<50): Underperforming

**Investment Tiers:**
- **PRIME** (85+): Immediate acquisition targets
- **STRONG** (75-84): High confidence investments
- **MODERATE** (65-74): Conditional opportunities
- **ACCEPTABLE** (50-64): Market-rate performers
- **UNDERPERFORMING** (<50): Avoid or turnaround candidates

## Benchmarking Approach

All comparisons are **bedroom-normalized** to ensure fair evaluation:
- Market averages calculated per bedroom count (1BR, 2BR, etc.)
- ADR distributions segmented by property size
- Prevents penalizing smaller properties or inflating larger ones

## Key Design Principles

1. **Market-relative scoring**: Properties compete within their bedroom segment, not globally
2. **Multi-dimensional**: No single metric dominates; balances income, stability, and growth potential
3. **Opportunity identification**: Rewards both current performance and upside potential
4. **Risk-adjusted**: Penalizes volatility (occupancy gaps, over-seasonality)
5. **Transparent weights**: Adjustable for different investment strategies (income vs. growth focus)

## Limitations & Considerations

- Assumes data accuracy and completeness (missing fields default to neutral scores)
- Does not account for: property age, capex requirements, regulatory risks, or market trends
- Historical performance may not predict future results
- Should be combined with qualitative analysis and local market expertise