# /// script
# dependencies = ["openpyxl"]
# ///
"""Regenerates the sample workbook model/battery_plan.xlsx.

Only the committed sample is built here. The model reads the workbook at run
time, so users can edit it in Excel directly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "model"))

import layout  # noqa: E402
from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Font  # noqa: E402
from reference_plan import DEFAULT_PARAMETERS  # noqa: E402

CALC_SHEET = "Calc"
CALC_FIRST_ROW = 5
CALC_LAST_ROW = 204
INPUTS_LAST_ROW = layout.PRICE_TABLE_FIRST_ROW + layout.PRICE_TABLE_CAPACITY - 1
CALC_HEADERS = (
    "DATETIME",
    "Price ($/MWh)",
    "Opening SOC (MWh)",
    "Storage change (MWh)",
    "Closing SOC (MWh)",
    "Grid energy (MWh)",
    "Power (MW)",
    "Revenue ($)",
    "Cumulative revenue ($)",
)
# Calc column feeding each Outputs column B..F.
OUTPUT_SOURCE_COLUMNS = ("B", "G", "E", "H", "I")


def build_inputs_cells() -> dict[str, object]:
    p = DEFAULT_PARAMETERS
    cells: dict[str, object] = {"A1": "Battery parameters"}
    parameter_rows = [
        ("Region", p["region"], "AEMO region ID"),
        ("Power", p["power_mw"], "MW"),
        ("Energy capacity", p["capacity_mwh"], "MWh"),
        ("Starting state of charge", p["start_soc_mwh"], "MWh"),
        ("Round-trip efficiency", p["efficiency"], "fraction, applied when charging"),
        ("Charge percentile", p["charge_percentile"], "fraction of the price range, 0 to 1"),
        ("Discharge percentile", p["discharge_percentile"], "fraction of the price range, 0 to 1"),
        ("Interval length", p["interval_hours"], "hours"),
    ]
    for offset, (label, value, note) in enumerate(parameter_rows):
        row = 2 + offset
        cells[f"A{row}"] = label
        cells[f"B{row}"] = value
        cells[f"C{row}"] = note
    header_row = layout.PRICE_TABLE_FIRST_ROW - 1
    cells[f"A{header_row}"] = "DATETIME"
    cells[f"B{header_row}"] = "Price ($/MWh)"
    return cells


def build_calc_cells() -> dict[str, object]:
    prices = f"Inputs!$B${layout.PRICE_TABLE_FIRST_ROW}:$B${INPUTS_LAST_ROW}"
    cells: dict[str, object] = {
        "A1": "Charge threshold ($/MWh)",
        "B1": f'=IF(COUNT({prices})=0,"",PERCENTILE({prices},Inputs!$B$7))',
        "A2": "Discharge threshold ($/MWh)",
        "B2": f'=IF(COUNT({prices})=0,"",PERCENTILE({prices},Inputs!$B$8))',
    }
    for offset, header in enumerate(CALC_HEADERS):
        cells[f"{chr(ord('A') + offset)}4"] = header

    for r in range(CALC_FIRST_ROW, CALC_LAST_ROW + 1):
        i = r + 7
        # Guard on the DATETIME text, never on price: 0 is a valid price.
        guard = f'IF($A{r}="","",'
        first = r == CALC_FIRST_ROW
        cells[f"A{r}"] = f'=IF(Inputs!$A{i}="","",Inputs!$A{i})'
        cells[f"B{r}"] = f"={guard}Inputs!$B{i})"
        cells[f"C{r}"] = (
            f'=IF($A{r}="","",Inputs!$B$5)' if first else f"={guard}E{r - 1})"
        )
        cells[f"D{r}"] = (
            f"={guard}IF(AND(B{r}<=$B$1,C{r}<Inputs!$B$4),"
            f"MIN(Inputs!$B$3*Inputs!$B$9*Inputs!$B$6,Inputs!$B$4-C{r}),"
            f"IF(AND(B{r}>=$B$2,C{r}>0),-MIN(Inputs!$B$3*Inputs!$B$9,C{r}),0)))"
        )
        cells[f"E{r}"] = f"={guard}C{r}+D{r})"
        cells[f"F{r}"] = f"={guard}IF(D{r}>0,-D{r}/Inputs!$B$6,-D{r}))"
        cells[f"G{r}"] = f"={guard}F{r}/Inputs!$B$9)"
        cells[f"H{r}"] = f"={guard}B{r}*F{r})"
        cells[f"I{r}"] = f"={guard}H{r})" if first else f"={guard}I{r - 1}+H{r})"
    return cells


def build_outputs_cells() -> dict[str, object]:
    cells: dict[str, object] = {}
    for offset, header in enumerate(layout.OUTPUT_COLUMNS):
        cells[f"{chr(ord('A') + offset)}1"] = header

    last_row = layout.OUTPUTS_FIRST_ROW + layout.PRICE_TABLE_CAPACITY - 1
    for o in range(layout.OUTPUTS_FIRST_ROW, last_row + 1):
        r = o + 3
        guard = f'IF(Calc!$A{r}="","",'
        cells[f"A{o}"] = f'=IF(Calc!$A{r}="","",Calc!$A{r})'
        for offset, source in enumerate(OUTPUT_SOURCE_COLUMNS):
            cells[f"{chr(ord('B') + offset)}{o}"] = f"={guard}Calc!{source}{r})"
    return cells


def write_cells(sheet, cells: dict[str, object], header_cells: list[str]) -> None:
    for coordinate, value in cells.items():
        sheet[coordinate] = value
    for coordinate in header_cells:
        sheet[coordinate].font = Font(bold=True)


def write_workbook(path: Path) -> None:
    workbook = Workbook()
    inputs = workbook.active
    inputs.title = layout.INPUTS_SHEET
    calc = workbook.create_sheet(CALC_SHEET)
    outputs = workbook.create_sheet(layout.OUTPUTS_SHEET)

    header_row = layout.PRICE_TABLE_FIRST_ROW - 1
    write_cells(inputs, build_inputs_cells(), ["A1", f"A{header_row}", f"B{header_row}"])
    # Text format keeps the DATETIME strings from being coerced into dates.
    for row in range(layout.PRICE_TABLE_FIRST_ROW, INPUTS_LAST_ROW + 1):
        inputs[f"A{row}"].number_format = "@"
    inputs.column_dimensions["A"].width = 28
    inputs.column_dimensions["B"].width = 14
    inputs.column_dimensions["C"].width = 36

    write_cells(calc, build_calc_cells(), [f"{chr(ord('A') + n)}4" for n in range(9)])
    write_cells(
        outputs,
        build_outputs_cells(),
        [f"{chr(ord('A') + n)}1" for n in range(len(layout.OUTPUT_COLUMNS))],
    )
    for sheet, count in ((calc, 9), (outputs, len(layout.OUTPUT_COLUMNS))):
        for n in range(count):
            sheet.column_dimensions[chr(ord("A") + n)].width = 22

    workbook.save(path)


if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "model" / layout.WORKBOOK_FILE
    write_workbook(target)
    print(target)
