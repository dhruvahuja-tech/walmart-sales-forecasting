
-- Dataset overview — rows, stores, depts, date range:

SELECT
    COUNT(*)                AS total_rows,
    COUNT(DISTINCT store)   AS total_stores,
    COUNT(DISTINCT dept)    AS total_depts,
    COUNT(DISTINCT date)    AS total_weeks,
    MIN(date)               AS start_date,
    MAX(date)               AS end_date
FROM train;



--  NULL count in features — markdowns will have many NULLs:

SELECT
    COUNT(*) FILTER (WHERE markdown1    IS NULL) AS null_md1,
    COUNT(*) FILTER (WHERE markdown2    IS NULL) AS null_md2,
    COUNT(*) FILTER (WHERE markdown3    IS NULL) AS null_md3,
    COUNT(*) FILTER (WHERE markdown4    IS NULL) AS null_md4,
    COUNT(*) FILTER (WHERE markdown5    IS NULL) AS null_md5,
    COUNT(*) FILTER (WHERE cpi          IS NULL) AS null_cpi,
    COUNT(*) FILTER (WHERE unemployment IS NULL) AS null_unemployment,
    COUNT(*)                                     AS total_rows
FROM features;



-- Negative sales — returns can cause negative weekly_sales:

SELECT
    COUNT(*)                                    AS negative_count,
    ROUND(MIN(weekly_sales)::NUMERIC, 2)        AS worst_value,
    ROUND(AVG(weekly_sales)
          FILTER (WHERE weekly_sales < 0)
          ::NUMERIC, 2)                         AS avg_negative
FROM train
WHERE weekly_sales < 0;


--  Store type breakdown — count, avg size:

SELECT
    type,
    COUNT(*)            AS store_count,
    ROUND(AVG(size))    AS avg_size_sqft,
    MIN(size)           AS min_size,
    MAX(size)           AS max_size
FROM stores
GROUP BY type
ORDER BY type;


-- Avg weekly sales by store type:

SELECT
    s.type,
    ROUND(AVG(t.weekly_sales)::NUMERIC, 2)      AS avg_weekly_sales,
    ROUND(SUM(t.weekly_sales)::NUMERIC, 2)      AS total_sales,
    ROUND(STDDEV(t.weekly_sales)::NUMERIC, 2)   AS sales_std_dev
FROM train t
JOIN stores s ON t.store = s.store
GROUP BY s.type
ORDER BY avg_weekly_sales DESC;


-- Holiday vs non-holiday avg sales comparison:

SELECT
    is_holiday,
    COUNT(*)                                    AS total_records,
    ROUND(AVG(weekly_sales)::NUMERIC, 2)        AS avg_weekly_sales,
    ROUND(MAX(weekly_sales)::NUMERIC, 2)        AS max_weekly_sales,
    ROUND(SUM(weekly_sales)::NUMERIC, 2)        AS total_sales
FROM train
GROUP BY is_holiday;

-- Top 10 departments by avg weekly sales:

SELECT
    dept,
    ROUND(AVG(weekly_sales)::NUMERIC, 2)    AS avg_weekly_sales,
    ROUND(SUM(weekly_sales)::NUMERIC, 2)    AS total_sales,
    COUNT(DISTINCT store)                   AS stores_with_dept
FROM train
GROUP BY dept
ORDER BY avg_weekly_sales DESC
LIMIT 10;


-- Compare avg sales: weeks with any markdown vs weeks without:

SELECT
    CASE
        WHEN f.markdown1 IS NOT NULL
          OR f.markdown2 IS NOT NULL
          OR f.markdown3 IS NOT NULL
          OR f.markdown4 IS NOT NULL
          OR f.markdown5 IS NOT NULL
        THEN 'Has Markdown'
        ELSE 'No Markdown'
    END                                             AS markdown_status,
    COUNT(*)                                        AS total_records,
    ROUND(AVG(t.weekly_sales)::NUMERIC, 2)          AS avg_weekly_sales
FROM train t
JOIN features f ON t.store = f.store AND t.date = f.date
GROUP BY markdown_status;