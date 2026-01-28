-- -------------------------------------------------------------------------
-- Common Table Expression
-- -------------------------------------------------------------------------

-- Step 1: Calculate market averages per bedroom category
WITH market_averages AS (
    SELECT 
        market_area,
        bedrooms,
        AVG(revenue) AS avg_revenue,
        AVG(occupancy) AS avg_occupancy,
        AVG(adr) AS avg_adr,
        COUNT(*) AS property_count
    FROM properties
    WHERE bedrooms IS NOT NULL 
      AND revenue IS NOT NULL
    GROUP BY market_area, bedrooms
),

-- Step 2: Rank properties within each market and bedroom category by revenue
ranked_properties AS (
    SELECT 
        p.property_id,
        p.title,
        p.market_area,
        p.bedrooms,
        p.revenue,
        p.occupancy,
        p.adr,
        ROW_NUMBER() OVER (
            PARTITION BY p.market_area, p.bedrooms 
            ORDER BY p.revenue DESC
        ) AS rank_in_category
    FROM properties p
    WHERE p.bedrooms IS NOT NULL 
      AND p.revenue IS NOT NULL
),

-- Step 3: Get top 3 properties per market/bedroom combination
top_properties AS (
    SELECT *
    FROM ranked_properties
    WHERE rank_in_category <= 3
)

-- Step 4: Join with market averages and calculate gaps
SELECT 
    tp.market_area,
    tp.bedrooms || 'BR' AS bedroom_category,
    tp.rank_in_category,
    tp.property_id,
    tp.title,
    
    tp.revenue::NUMERIC(10,2) AS property_revenue,
    tp.occupancy::NUMERIC(5,4) AS property_occupancy,
    tp.adr::NUMERIC(10,2) AS property_adr,
    
    ma.avg_revenue::NUMERIC(10,2) AS market_avg_revenue,
    ma.avg_occupancy::NUMERIC(5,4) AS market_avg_occupancy,
    ma.avg_adr::NUMERIC(10,2) AS market_avg_adr,
    
    -- Gaps (Performance vs Average)
    (tp.revenue - ma.avg_revenue)::NUMERIC(10,2) AS revenue_gap,
    (tp.occupancy - ma.avg_occupancy)::NUMERIC(5,4) AS occupancy_gap,
    (tp.adr - ma.avg_adr)::NUMERIC(10,2) AS adr_gap,
    
    ROUND(((tp.revenue - ma.avg_revenue) / ma.avg_revenue * 100)::NUMERIC, 2) AS revenue_vs_avg_pct,
    
    ma.property_count AS total_properties_in_category
    
FROM top_properties tp
JOIN market_averages ma 
    ON tp.market_area = ma.market_area 
    AND tp.bedrooms = ma.bedrooms

ORDER BY 
    tp.market_area,
    tp.bedrooms,
    tp.rank_in_category;



-- -------------------------------------------------------------------------
-- Window Function
-- -------------------------------------------------------------------------
SELECT 
    market_area,
    bedrooms || 'BR' AS bedroom_category,
    rank_in_category,
    property_id,
    title,

    revenue::NUMERIC(10,2) AS property_revenue,
    occupancy::NUMERIC(5,4) AS property_occupancy,
    adr::NUMERIC(10,2) AS property_adr,

    market_avg_revenue::NUMERIC(10,2),
    market_avg_occupancy::NUMERIC(5,4),
    market_avg_adr::NUMERIC(10,2),

    -- Performance Gaps
    (revenue - market_avg_revenue)::NUMERIC(10,2) AS revenue_gap,
    (occupancy - market_avg_occupancy)::NUMERIC(5,4) AS occupancy_gap,
    (adr - market_avg_adr)::NUMERIC(10,2) AS adr_gap,

    -- Percentage Performance vs Average
    ROUND(
        ((revenue - market_avg_revenue) / market_avg_revenue * 100)::NUMERIC,
        2
    ) AS revenue_vs_avg_pct,

    total_properties_in_category

FROM (
    SELECT 
        p.property_id,
        p.title,
        p.market_area,
        p.bedrooms,
        p.revenue,
        p.occupancy,
        p.adr,

        -- Ranking per category
        ROW_NUMBER() OVER (
            PARTITION BY p.market_area, p.bedrooms 
            ORDER BY p.revenue DESC
        ) AS rank_in_category,

        -- Market averages (window functions)
        AVG(p.revenue) OVER (PARTITION BY p.market_area, p.bedrooms) AS market_avg_revenue,
        AVG(p.occupancy) OVER (PARTITION BY p.market_area, p.bedrooms) AS market_avg_occupancy,
        AVG(p.adr) OVER (PARTITION BY p.market_area, p.bedrooms) AS market_avg_adr,

        COUNT(*) OVER (PARTITION BY p.market_area, p.bedrooms) AS total_properties_in_category

    FROM properties p
    WHERE p.bedrooms IS NOT NULL 
      AND p.revenue IS NOT NULL
) ranked
WHERE rank_in_category <= 3
ORDER BY market_area, bedrooms, rank_in_category;
