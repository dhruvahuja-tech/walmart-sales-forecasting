 CTE 1: Store performance t — label each store as
--         High / Mid / Low performer based on total sales

WITH store_sales AS (
    -- Step 1: Total sales per store
    SELECT
        t.store,
        s.type                                      AS store_type,
        s.size,
        ROUND(SUM(t.weekly_sales)::NUMERIC, 2)      AS total_sales
    FROM train t
    JOIN stores s ON t.store = s.store
    GROUP BY t.store, s.type, s.size
),
percentiles AS (
    -- Step 2: Calculate 33rd and 66th percentile thresholds
    -- PERCENTILE_CONT finds the value at a given percentile
    SELECT
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY total_sales) AS p33,
        PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY total_sales) AS p66
    FROM store_sales
)
-- Step 3: Label each store based on which band it falls into
SELECT
    ss.store,
    ss.store_type,
    ss.size,
    ss.total_sales,
    CASE
        WHEN ss.total_sales >= p.p66 THEN 'High Performer'
        WHEN ss.total_sales >= p.p33 THEN 'Mid Performer'
        ELSE                               'Low Performer'
    END AS performance_tier
FROM store_sales ss
CROSS JOIN percentiles p        -- CROSS JOIN adds percentile columns to every row
ORDER BY ss.total_sales DESC;


-- Combines all 3 tables into one clean view:

CREATE OR REPLACE VIEW walmart_master AS
SELECT
    -- From train (core sales data)
    t.store,
    t.dept,
    t.date,
    t.weekly_sales,
    t.is_holiday,

    -- From stores (store metadata)
    s.type          AS store_type,
    s.size          AS store_size,

    -- From features (external factors)
    f.temperature,
    f.fuel_price,
    f.markdown1,
    f.markdown2,
    f.markdown3,
    f.markdown4,
    f.markdown5,
    f.cpi,
    f.unemployment
FROM train t
JOIN stores   s ON t.store = s.store
JOIN features f ON t.store = f.store
                AND t.date  = f.date;

SELECT COUNT(*) FROM walmart_master;