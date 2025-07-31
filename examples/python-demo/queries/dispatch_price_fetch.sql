SELECT
    settlementdate AS "SETTLEMENTDATE",
    regionid AS "REGIONID",
    rrp AS "RRP"
FROM mms.dispatchprice
WHERE
    settlementdate BETWEEN (
        pd_forecast.predispatchseqno2rundatetime(
            (
                SELECT max(predispatchprice.predispatchseqno)
                FROM mms.predispatchprice
            )
        )
        - interval '8 days'
    ) AND pd_forecast.predispatchseqno2rundatetime(
        (
            SELECT max(predispatchprice.predispatchseqno)
            FROM mms.predispatchprice
        )
    )
    AND intervention = 0
