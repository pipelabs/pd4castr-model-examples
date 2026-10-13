-- The latest half-hour boundary with a dispatch price. The value changes
-- every 30 minutes, which triggers a fresh fetch and a model run.
SELECT
    date_trunc('hour', max(settlementdate))
    + interval '30 minutes'
    * floor(extract(MINUTE FROM max(settlementdate)) / 30) AS latest_half_hour
FROM mms.dispatchprice
