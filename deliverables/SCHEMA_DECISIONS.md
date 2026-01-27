# Schema Design Decisions

## Overview
The database schema is designed to efficiently store and query vacation rental property data across multiple markets while balancing normalization with performance requirements for a property scoring algorithm.

## Core Design Principles

### 1. Single Market Table Approach
Rather than creating separate tables per market (e.g., `properties_indianapolis`, `properties_blue_ridge`), all properties are stored in a single `properties` table with a `market_area` indexed column. This decision was made because:
- The dataset contains only three markets with manageable data volumes
- A unified table simplifies cross-market analysis and scoring comparisons
- Market-specific queries remain performant through indexing
- Future scalability can be achieved through partitioning if needed

### 2. Selective Normalization Strategy

**Properties Table (Denormalized Elements)**
The main `properties` table intentionally keeps boolean amenity flags (e.g., `has_aircon`, `has_pool`, `system_gym`) denormalized because:
- Amenities are frequently queried in scoring algorithms and property filtering
- Avoiding joins for 20+ boolean checks significantly improves query performance
- The data is simple (boolean), non-volatile, and doesn't create update anomalies
- Storage overhead is minimal compared to join overhead

**Normalized Tables**
Three separate tables were created for logically distinct data groups:

- **`property_reviews`**: Review statistics and guest demographic data normalized into a 1:1 relationship
  - Rationale: Review analytics are not always needed for basic property queries
  - Reduces main table width and improves cache efficiency
  - Cleanly separates performance metrics from property attributes

- **`property_amenities`**: Raw amenity strings stored as JSONB
  - Rationale: The `amenities` column contains unstructured comma-separated text requiring parsing
  - JSONB allows flexible querying while maintaining raw data integrity
  - Prevents cluttering the main table with unparsed text blobs
  - Enables future amenity taxonomy development without schema changes

- **`investment_scores`**: Computed scoring metrics
  - Rationale: Separates calculated/derived data from source data
  - Allows score recalculation without touching property records
  - Clear audit trail for scoring algorithm changes

### 3. Data Deduplication and Column Consolidation

Extensive column consolidation was performed to eliminate redundancy:

| Removed Column | Reason | Replacement |
|----------------|--------|-------------|
| `HAS_HOTTUB` | Duplicate functionality | `SYSTEM_JACUZZI` |
| `Listing Name`, `name`, `title` (3 columns) | Same data | `title` |
| `Bedrooms` (duplicate) | Exact duplicate | `BEDROOMS` |
| `total_reviews` | Redundant | `review_total_reviews` |
| `url` | Duplicate | `airbnb_listing_url` |
| `latitude`, `longitude` (duplicates) | Redundant columns | Original lat/long fields |
| `is_super_host` | Duplicate | `superhost` |
| `beds` | Redundant | `number_of_beds` |
| `roomType` | Redundant | `propertyType` |
| `reviewsCount` | Duplicate | `review_total_reviews` |

This reduced the column count from 98 to approximately 60 meaningful attributes across all tables.

### 4. Enum-Like Fields (Not Normalized)

Fields like `price_tier` and `data_quality_category` are stored as strings rather than separate reference tables:
- Current dataset has limited distinct values (3-5 categories each)
- Premature normalization would add join complexity for minimal benefit
- **Future consideration**: As the dataset grows, these should migrate to ENUM types or reference tables for data integrity and storage efficiency

### 5. Data Type Choices

- **Decimals for financials**: `revenue`, `adr`, `cleaning_fee` use `Float(asdecimal=True)` to avoid floating-point precision issues
- **JSONB for amenities**: Enables indexing and querying of semi-structured data without rigid schema constraints
- **Indexed columns**: `property_id`, `market_area` indexed for frequent query patterns
- **Boolean defaults**: All boolean amenity flags default to `False` for consistent null handling

## Schema Relationships

```
properties (1) ←→ (1) property_reviews
properties (1) ←→ (1) property_amenities  
properties (1) ←→ (1) investment_scores
```

All relationships are 1:1 with cascade deletion to maintain referential integrity. The `property_id` serves as the natural key across all tables.

## Trade-offs and Future Considerations

**Current Trade-offs:**
- Denormalized boolean amenities favor read performance over strict normalization
- String-based enums sacrifice some integrity for implementation simplicity
- Single-table market storage may require partitioning at scale

**Future Improvements:**
- Implement table partitioning by `market_area` when data exceeds 100K+ properties per market
- Create reference tables for `price_tier` and `data_quality_category` when values stabilize
- Build amenity taxonomy table from parsed `amenities` JSONB data
- Consider materialized views for common scoring queries