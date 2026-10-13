-- Seasonal-naive baseline: the forecast for each half-hour and region is the
-- dispatch price at the same half-hour one week earlier.
--
-- The entrypoint runs this file with the DuckDB CLI in a directory holding
-- the downloaded input (dispatch_price.json). Whatever lands in output.json
-- is uploaded as the model output.

-- How far back the forecast looks: each half-hour repeats the price from
-- this long before it.
SET VARIABLE lag = INTERVAL 7 DAY;

COPY (
    -- The input as fetched: one row per 5-minute interval and region.
    -- Declaring the columns keeps the parse the same across DuckDB versions.
    WITH dispatch_price AS (
        SELECT
            -- The input is in NEM time (UTC+10) and the time zone is dropped:
            -- '2026-10-13T17:00:00.000+10:00' -> TIMESTAMP '2026-10-13 17:00:00'
            left(SETTLEMENTDATE, 19)::TIMESTAMP AS settlementdate,
            REGIONID AS region,
            RRP AS price
        FROM read_json(
            'dispatch_price.json',
            columns = {
                SETTLEMENTDATE: 'VARCHAR', REGIONID: 'VARCHAR', RRP: 'DOUBLE'
            }
        )
    ),

    -- The price of the 5-minute interval that ends on each half-hour
    -- (HH:00 and HH:30).
    half_hourly_price AS (
        SELECT *
        FROM dispatch_price
        WHERE minute(settlementdate) IN (0, 30)
    ),

    latest AS (
        SELECT max(settlementdate) AS settlementdate
        FROM half_hourly_price
    )

    -- Forecast the 48 half-hours after the latest price by moving one day of
    -- prices from one lag earlier forward by the lag. pd4castr expects UTC,
    -- and NEM time is UTC+10 all year.
    SELECT
        strftime(
            p.settlementdate + getvariable('lag') - INTERVAL 10 HOUR,
            '%Y-%m-%dT%H:%M:%SZ'
        ) AS forecast_datetime,
        max(p.price) FILTER (WHERE p.region = 'NSW1') AS nsw1,
        max(p.price) FILTER (WHERE p.region = 'QLD1') AS qld1,
        max(p.price) FILTER (WHERE p.region = 'SA1') AS sa1,
        max(p.price) FILTER (WHERE p.region = 'TAS1') AS tas1,
        max(p.price) FILTER (WHERE p.region = 'VIC1') AS vic1
    FROM half_hourly_price AS p, latest
    WHERE
        p.settlementdate > latest.settlementdate - getvariable('lag')
        AND p.settlementdate
        <= latest.settlementdate - getvariable('lag') + INTERVAL 1 DAY
    GROUP BY p.settlementdate
    ORDER BY p.settlementdate
) TO 'output.json' (FORMAT JSON, ARRAY true);
