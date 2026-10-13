from layout import (
    INPUTS_SHEET,
    PRICE_TABLE_CAPACITY,
    PRICE_TABLE_DATETIME_COLUMN,
    PRICE_TABLE_FIRST_ROW,
    PRICE_TABLE_PRICE_COLUMN,
    REGION_CELL,
)


def get_region(workbook) -> str:
    value = workbook[INPUTS_SHEET][REGION_CELL].value
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"{INPUTS_SHEET}!{REGION_CELL} must hold a region ID such as NSW1"
        )
    return value.strip()


def build_price_table(price_rows: list[dict], region: str) -> list[tuple[str, float]]:
    table = []
    for index, row in enumerate(price_rows):
        if row.get("REGIONID") != region:
            continue
        datetime_value = row.get("DATETIME")
        price = row.get("PD_RRP")
        if (
            not isinstance(datetime_value, str)
            or isinstance(price, bool)
            or not isinstance(price, (int, float))
        ):
            raise ValueError(
                f"Input row {index} needs a string DATETIME and a numeric PD_RRP"
            )
        table.append((datetime_value, float(price)))

    if not table:
        regions = sorted({str(row.get("REGIONID")) for row in price_rows})
        raise ValueError(f"No input rows for region {region}; regions present: {regions}")

    # One query, one ISO format: string order is chronological order.
    table.sort(key=lambda pair: pair[0])

    seen = set()
    for datetime_value, _ in table:
        if datetime_value in seen:
            raise ValueError(f"Duplicate DATETIME {datetime_value} for region {region}")
        seen.add(datetime_value)

    if len(table) > PRICE_TABLE_CAPACITY:
        raise ValueError(
            f"{len(table)} intervals for {region} exceed the workbook's price table capacity of {PRICE_TABLE_CAPACITY} rows"
        )
    return table


def write_workbook_inputs(workbook, price_table: list[tuple[str, float]], path) -> None:
    sheet = workbook[INPUTS_SHEET]

    # PERCENTILE reads the whole range, so rows left over in a user-supplied
    # workbook would skew the thresholds.
    for offset in range(PRICE_TABLE_CAPACITY):
        row = PRICE_TABLE_FIRST_ROW + offset
        sheet.cell(row=row, column=PRICE_TABLE_DATETIME_COLUMN).value = None
        sheet.cell(row=row, column=PRICE_TABLE_PRICE_COLUMN).value = None

    for offset, (datetime_value, price) in enumerate(price_table):
        row = PRICE_TABLE_FIRST_ROW + offset
        sheet.cell(row=row, column=PRICE_TABLE_DATETIME_COLUMN).value = datetime_value
        sheet.cell(row=row, column=PRICE_TABLE_PRICE_COLUMN).value = price

    workbook.save(path)
