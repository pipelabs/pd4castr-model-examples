import tempfile
import time
from pathlib import Path

import openpyxl

from layout import WORKBOOK_FILE
from load_input import load_price_rows
from recalculate import run_recalculation
from upload_output import send_output
from workbook_inputs import build_price_table, get_region, write_workbook_inputs
from workbook_outputs import load_output_rows


def run_workbook(price_rows: list[dict]) -> list[dict]:
    workbook = openpyxl.load_workbook(Path(__file__).resolve().parent / WORKBOOK_FILE)
    region = get_region(workbook)
    table = build_price_table(price_rows, region)
    print(f"Region {region}: {len(table)} intervals")

    with tempfile.TemporaryDirectory() as tmp:
        # soffice keeps the input's basename, so input and output need separate dirs.
        in_dir = Path(tmp) / "in"
        out_dir = Path(tmp) / "out"
        in_dir.mkdir()
        out_dir.mkdir()

        source = in_dir / WORKBOOK_FILE
        write_workbook_inputs(workbook, table, source)

        print("Recalculating workbook with LibreOffice")
        started = time.monotonic()
        converted = run_recalculation(source, out_dir)
        print(f"Recalculation finished in {time.monotonic() - started:.1f} s")

        return load_output_rows(converted, table)


def run_model() -> None:
    rows = run_workbook(load_price_rows())
    send_output(rows)


if __name__ == "__main__":
    run_model()
