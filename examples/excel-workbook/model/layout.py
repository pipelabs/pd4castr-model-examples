# Every cell address the Python code touches lives here, so changing the
# workbook layout means editing this file and scripts/build_workbook.py only.
WORKBOOK_FILE = "battery_plan.xlsx"
INPUTS_SHEET = "Inputs"
OUTPUTS_SHEET = "Outputs"
REGION_CELL = "B2"
PRICE_TABLE_FIRST_ROW = 12
PRICE_TABLE_CAPACITY = 200
PRICE_TABLE_DATETIME_COLUMN = 1  # A
PRICE_TABLE_PRICE_COLUMN = 2  # B
OUTPUTS_FIRST_ROW = 2
# Columns A..F of the Outputs sheet, in order.
OUTPUT_COLUMNS = (
    "forecast_datetime",
    "price",
    "power_mw",
    "soc_mwh",
    "revenue",
    "cumulative_revenue",
)
