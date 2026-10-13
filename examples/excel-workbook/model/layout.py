# Every cell address the model touches lives here: a layout change edits this
# file and scripts/build_workbook.py, nothing else.
WORKBOOK_FILE = "battery_plan.xlsx"
INPUTS_SHEET = "Inputs"
OUTPUTS_SHEET = "Outputs"
REGION_CELL = "B2"
PRICE_TABLE_FIRST_ROW = 12
PRICE_TABLE_CAPACITY = 200
PRICE_TABLE_DATETIME_COLUMN = 1
PRICE_TABLE_PRICE_COLUMN = 2
OUTPUTS_FIRST_ROW = 2
OUTPUT_FIRST_COLUMN = 1
# Order matches the Outputs sheet's columns.
OUTPUT_COLUMNS = (
    "forecast_datetime",
    "price",
    "power_mw",
    "soc_mwh",
    "revenue",
    "cumulative_revenue",
)
