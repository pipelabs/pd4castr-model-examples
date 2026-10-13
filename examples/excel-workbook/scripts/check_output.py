"""Compares a pd4castr test output file against the reference battery plan.

Usage: python3 scripts/check_output.py [--input PATH] [--output PATH]
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_plan import build_reference_plan  # noqa: E402

EXAMPLE_DIR = Path(__file__).resolve().parent.parent
NUMERIC_KEYS = ("price", "power_mw", "soc_mwh", "revenue", "cumulative_revenue")
TOLERANCE = 1e-6
MAX_REPORTED = 20


def find_latest_output(output_dir: Path) -> Path | None:
    # Newest by the epoch ms in the filename, not mtime (checkouts reset mtime).
    best = None
    best_stamp = -1
    for path in output_dir.glob("output-*.json"):
        match = re.fullmatch(r"output-(\d+)\.json", path.name)
        if match and int(match.group(1)) > best_stamp:
            best, best_stamp = path, int(match.group(1))
    return best


def load_json(path: Path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def check_output(price_rows, output_rows) -> list[str]:
    if not isinstance(output_rows, list):
        return ["output is not a JSON array"]

    reference = build_reference_plan(price_rows)
    mismatches = []
    if len(output_rows) != len(reference):
        mismatches.append(
            f"row count is {len(output_rows)}, expected {len(reference)}"
        )

    for index, (expected, actual) in enumerate(zip(reference, output_rows)):
        if not isinstance(actual, dict):
            mismatches.append(f"row {index}: not an object")
            continue
        if actual.get("forecast_datetime") != expected["forecast_datetime"]:
            mismatches.append(
                f"row {index}: forecast_datetime is {actual.get('forecast_datetime')!r}, expected {expected['forecast_datetime']!r}"
            )
        for key in NUMERIC_KEYS:
            value = actual.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                mismatches.append(f"row {index}: {key} is {value!r}, expected a number")
            # Within tolerance rather than equal: idle rows can be -0.0 versus 0.
            elif abs(value - expected[key]) > TOLERANCE:
                mismatches.append(
                    f"row {index}: {key} is {value}, expected {expected[key]}"
                )
    return mismatches


def run_check() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=EXAMPLE_DIR / "test_input" / "predispatch_price.json")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    output_path = args.output or find_latest_output(EXAMPLE_DIR / "test_output")
    if output_path is None:
        print("No output file found in test_output/; run `yarn pd4castr test` first")
        return 1

    price_rows = load_json(args.input)
    mismatches = check_output(price_rows, load_json(output_path))
    if mismatches:
        for message in mismatches[:MAX_REPORTED]:
            print(message)
        print(f"{len(mismatches)} mismatches in {output_path}")
        return 1

    print(f"OK: {len(load_json(output_path))} rows match the reference plan")
    return 0


if __name__ == "__main__":
    sys.exit(run_check())
