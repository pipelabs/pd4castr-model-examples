"""Pure-Python reference for the battery plan the workbook calculates.

check_output.py compares model output against this. build_workbook.py reads
DEFAULT_PARAMETERS for the sample workbook's inputs, so editing a workbook
parameter means editing DEFAULT_PARAMETERS here too and re-running
build_workbook.py.
"""

import math

DEFAULT_PARAMETERS = {
    "region": "NSW1",
    "power_mw": 50.0,
    "capacity_mwh": 100.0,
    "start_soc_mwh": 50.0,
    "efficiency": 0.85,
    "charge_percentile": 0.25,
    "discharge_percentile": 0.75,
    "interval_hours": 0.5,
}


def build_percentile(values, fraction):
    """PERCENTILE.INC interpolation, as Excel and LibreOffice compute it."""
    s = sorted(values)
    k = fraction * (len(s) - 1)
    f = math.floor(k)
    d = k - f
    if d == 0:
        return s[f]
    return s[f] + d * (s[f + 1] - s[f])


def build_reference_plan(price_rows, parameters=DEFAULT_PARAMETERS):
    region = parameters["region"]
    power = parameters["power_mw"]
    cap = parameters["capacity_mwh"]
    eff = parameters["efficiency"]
    hours = parameters["interval_hours"]

    rows = sorted(
        (r for r in price_rows if r["REGIONID"] == region), key=lambda r: r["DATETIME"]
    )
    prices = [float(r["PD_RRP"]) for r in rows]
    charge_thr = build_percentile(prices, parameters["charge_percentile"])
    discharge_thr = build_percentile(prices, parameters["discharge_percentile"])

    # Same operations in the same order as the Calc sheet formulas, so float
    # results agree to well within the checker's tolerance.
    soc = parameters["start_soc_mwh"]
    cumulative = 0.0
    plan = []
    for row, price in zip(rows, prices):
        if price <= charge_thr and soc < cap:
            delta = min(power * hours * eff, cap - soc)
        elif price >= discharge_thr and soc > 0:
            delta = -min(power * hours, soc)
        else:
            delta = 0.0
        soc = soc + delta
        grid = -delta / eff if delta > 0 else -delta
        power_mw = grid / hours
        revenue = price * grid
        cumulative = cumulative + revenue
        plan.append(
            {
                "forecast_datetime": row["DATETIME"],
                "price": price,
                "power_mw": power_mw,
                "soc_mwh": soc,
                "revenue": revenue,
                "cumulative_revenue": cumulative,
            }
        )
    return plan
