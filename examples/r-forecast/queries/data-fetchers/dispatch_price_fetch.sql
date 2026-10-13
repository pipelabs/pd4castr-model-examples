-- The average dispatch price of each half-hour in the last 8 weeks, all
-- regions. SETTLEMENTDATE is the time the half-hour ends.
WITH bounds AS (
    -- The latest half-hour boundary, as in dispatch_price_check.sql. Only
    -- half-hours that end by then have all 6 of their 5-minute prices.
    SELECT
        date_trunc('hour', max(settlementdate))
        + interval '30 minutes'
        * floor(extract(MINUTE FROM max(settlementdate)) / 30) AS last_half_hour
    FROM mms.dispatchprice
),

dispatch AS (
    -- A 5-minute interval's settlementdate is its end, so shifting it back
    -- 5 minutes gives its start.
    SELECT
        dp.settlementdate - interval '5 minutes' AS interval_start,
        dp.regionid,
        dp.rrp
    FROM mms.dispatchprice AS dp
    CROSS JOIN bounds
    WHERE
        dp.settlementdate > bounds.last_half_hour - interval '56 days'
        AND dp.settlementdate <= bounds.last_half_hour
        AND dp.intervention = 0
)

SELECT
    date_trunc('hour', interval_start)
    + interval '30 minutes'
    * (floor(extract(MINUTE FROM interval_start) / 30) + 1) AS "SETTLEMENTDATE",
    regionid AS "REGIONID",
    avg(rrp)::double precision AS "RRP"
FROM dispatch
GROUP BY 1, 2
ORDER BY 1, 2
