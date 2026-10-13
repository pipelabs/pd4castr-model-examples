-- Every 5-minute dispatch price for the last 7 days, all regions.
SELECT
    settlementdate AS "SETTLEMENTDATE",
    regionid AS "REGIONID",
    rrp AS "RRP"
FROM mms.dispatchprice
WHERE
    settlementdate > (
        SELECT max(settlementdate) FROM mms.dispatchprice
    ) - interval '7 days'
    AND intervention = 0
ORDER BY settlementdate ASC, regionid ASC
