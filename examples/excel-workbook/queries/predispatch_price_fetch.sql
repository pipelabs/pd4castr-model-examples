SELECT
    predispatchprice.predispatchseqno AS "PREDISPATCHSEQNO",
    predispatchprice.datetime AS "DATETIME",
    predispatchprice.regionid AS "REGIONID",
    predispatchprice.rrp AS "PD_RRP"
FROM mms.predispatchprice
WHERE
    mms.predispatchprice.predispatchseqno = (
        SELECT max(sub.predispatchseqno)
        FROM mms.predispatchprice AS sub
    )
    AND predispatchprice.intervention = 0
