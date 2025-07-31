SELECT
    predispatchregionsum.predispatchseqno AS "PREDISPATCHSEQNO",
    predispatchregionsum.datetime AS "DATETIME",
    predispatchregionsum.regionid AS "REGIONID",
    predispatchregionsum.totaldemand AS "TOTALDEMAND",
    predispatchregionsum.dispatchableload AS "DISPATCHABLELOAD",
    predispatchregionsum.netinterchange AS "NETINTERCHANGE",
    predispatchregionsum.ss_solar_clearedmw AS "SS_SOLAR_CLEAREDMW",
    predispatchregionsum.ss_solar_uigf AS "SS_SOLAR_UIGF",
    predispatchregionsum.ss_wind_clearedmw AS "SS_WIND_CLEAREDMW",
    predispatchregionsum.ss_wind_uigf AS "SS_WIND_UIGF",
    predispatchregionsum.totalintermittentgeneration
        AS "TOTALINTERMITTENTGENERATION",
    predispatchregionsum.dispatchablegeneration AS "DISPATCHABLEGENERATION",
    predispatchregionsum.semischedule_clearedmw AS "SEMISCHEDULE_CLEAREDMW",
    predispatchregionsum.availablegeneration AS "AVAILABLEGENERATION",
    predispatchregionsum.uigf AS "UIGF",
    predispatchregionsum.demand_and_nonschedgen AS "DEMAND_AND_NONSCHEDGEN"
FROM mms.predispatchregionsum
WHERE
    predispatchregionsum.predispatchseqno = (
        SELECT max(predispatchprice.predispatchseqno)
        FROM mms.predispatchprice
    )
    AND predispatchregionsum.intervention = 0
