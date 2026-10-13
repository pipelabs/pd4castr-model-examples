# Excel - Battery Workbook

This example is a model for [pd4castr](https://pd4castr.com.au/), a platform
that runs forecasting models on Australian electricity market data, and the
model's calculation lives in an Excel workbook. Read it if your model is a
spreadsheet and you want to run it on pd4castr without rewriting the formulas in
code.

The sample workbook, `model/battery_plan.xlsx`, plans when a battery charges and
discharges, and the revenue that plan earns. The battery sits in one region of
the National Electricity Market (NEM), which has five regions: `NSW1`, `QLD1`,
`SA1`, `TAS1` and `VIC1`. Its prices come from predispatch, the price forecast
that the Australian Energy Market Operator (AEMO) publishes for each half-hour
interval up to the end of the next trading day.

## How a run works

The model runs in a Docker container that pd4castr starts. An input is a data
file that pd4castr fetches before each run, and `.pd4castrrc.json` declares this
model's one input, `predispatch_price`. pd4castr passes the container one
download URL per input, such as `INPUT_PREDISPATCH_PRICE_URL`, and one upload
URL, `OUTPUT_URL`, in environment variables. The
[pd4castr documentation](https://docs.v2.pd4castr.com.au) covers inputs and the
model configuration file.

Each row of the `predispatch_price` input holds a region (`REGIONID`), the
interval's time (`DATETIME`) and the forecast price (`PD_RRP`). Each run goes
through these stages, which `model/main.py` drives:

1. The model downloads the `predispatch_price` input, which holds every interval
   for all five regions.
2. The model reads the region from the workbook's `Inputs!B2` cell and keeps
   only that region's rows.
3. The model writes each interval's `DATETIME` and price into the price table on
   the Inputs sheet.
4. LibreOffice opens the workbook without a display, recalculates every formula,
   and saves a copy.
5. The model reads the Outputs sheet of the copy and uploads one JSON row per
   interval to `OUTPUT_URL`.

By default, LibreOffice reuses the results cached in an `.xlsx` file instead of
recalculating them. The model sets LibreOffice to recalculate every formula on
load, so the uploaded values always come from the current run's prices.

## The sample workbook

The battery charges when the price is low and discharges when the price is high.
The workbook sets "low" and "high" as two price thresholds, each a percentile of
all the prices in the run. It spreads the calculation over three sheets:

- **Inputs** holds the battery parameters and the price table. The price table
  fills `A12:B211`, which leaves room for 200 intervals.
- **Calc** works out the two price thresholds, then each interval's state of
  charge, grid energy, power and revenue.
- **Outputs** lays out one row per interval in the columns the model uploads.

`scripts/build_workbook.py` writes the battery parameters into column B of the
Inputs sheet:

| Cell | Parameter                | Sample value |
| ---- | ------------------------ | ------------ |
| `B2` | Region                   | `NSW1`       |
| `B3` | Power                    | 50 MW        |
| `B4` | Energy capacity          | 100 MWh      |
| `B5` | Starting state of charge | 50 MWh       |
| `B6` | Round-trip efficiency    | 0.85         |
| `B7` | Charge percentile        | 0.25         |
| `B8` | Discharge percentile     | 0.75         |
| `B9` | Interval length          | 0.5 hours    |

With the sample values, the charge threshold is the 25th percentile of the
prices and the discharge threshold is the 75th, calculated with Excel's
`PERCENTILE` function. In each interval, the battery charges at full power when
the price is at or below the charge threshold, and discharges at full power when
the price is at or above the discharge threshold. The battery never charges past
its energy capacity or discharges below empty.

Grid energy is the energy that flows between the battery and the grid in an
interval. It is positive when the battery discharges into the grid and negative
when the battery charges from it. The workbook applies the whole round-trip loss
when the battery charges. With the sample efficiency in `B6`, the battery stores
0.85 MWh for each 1 MWh it draws, and sends all the energy it discharges to the
grid. Revenue is the price times grid energy. NEM prices can fall below zero, so
charging costs money at a positive price and earns money at a negative one.

Each output row holds these values:

- `forecast_datetime` is the interval's `DATETIME`, copied unchanged.
- `price` is the predispatch price in $/MWh.
- `power_mw` is grid energy divided by the interval length.
- `soc_mwh` is the state of charge at the end of the interval.
- `revenue` and `cumulative_revenue` are in dollars.

## Running the example locally

You need Docker, Node.js, Yarn and Python 3.10 or later. Run each command from
this directory.

1. Install the pd4castr CLI:

   ```bash
   yarn install
   ```

2. Run the model against the sample input in `test_input/`:

   ```bash
   yarn pd4castr test
   ```

   Expect `Model output validation passed`. The CLI writes the output to
   `test_output/output-<timestamp>.json`.

3. Compare the newest output in `test_output/` with the reference plan, which
   `scripts/reference_plan.py` calculates from the same input in plain Python:

   ```bash
   python3 scripts/check_output.py
   ```

   Expect `OK: 32 rows match the reference plan`.

`yarn pd4castr test` runs the container without CPU or memory limits. Under the
limits
`docker run --platform linux/amd64 --cpus=0.25 --memory=512m --memory-swap=512m`,
a run of the sample workbook takes 10 to 15 s, and LibreOffice accounts for 8 to
11 s of that. Memory use peaks at 220 to 380 MiB. The image is 489 MB. Compare
your own workbook against these figures.

To repeat the measurement, run the image that `yarn pd4castr test` builds, which
it tags `pd4castr/excel-workbook-local:<timestamp>`, with those limits. Point
`INPUT_PREDISPATCH_PRICE_URL` at a local server that serves
`test_input/predispatch_price.json`, and point `OUTPUT_URL` at a server that
accepts a PUT.

## Using your own workbook

`model/layout.py` holds every sheet name and cell address the model uses. To run
your own workbook, edit `model/layout.py` to match it, then update the outputs
in `.pd4castrrc.json`:

1. Save your workbook as `.xlsx` in `model/`.
2. Set `WORKBOOK_FILE` in `model/layout.py` to the workbook's file name.
3. Set `INPUTS_SHEET` and `OUTPUTS_SHEET` to the names of your input and output
   sheets.
4. Set `REGION_CELL` to the address of the region cell on the input sheet, such
   as `"B2"`.
5. Set `PRICE_TABLE_FIRST_ROW` to the price table's first data row, below any
   header. Set `PRICE_TABLE_DATETIME_COLUMN` and `PRICE_TABLE_PRICE_COLUMN` to
   the column numbers of its `DATETIME` and price columns, counting column A
   as 1.
6. Set `PRICE_TABLE_CAPACITY` to the number of rows in your price table. The
   model clears that many rows before it writes the prices.
7. Set `OUTPUTS_FIRST_ROW` to the output sheet's first data row, and
   `OUTPUT_FIRST_COLUMN` to the column number of its first column, counting
   column A as 1.
8. Fill the output sheet with one row per interval, in price-table order. The
   first column holds the interval's `DATETIME`, and every other column must
   calculate to a number.
9. Make every output row past the last interval calculate to empty text. The
   sample guards each formula with `IF(<datetime cell>="","",<formula>)`,
   because a plain reference to an empty cell calculates to 0.
10. List a key for each output sheet column in `OUTPUT_COLUMNS`, in sheet order.
    Keep `forecast_datetime` as the first key, since pd4castr reads each row's
    time from it.
11. Make the `outputs` list in `.pd4castrrc.json` hold one entry for each key in
    `OUTPUT_COLUMNS` after `forecast_datetime`, with the same `key`, and remove
    the sample entries your sheet doesn't produce. pd4castr rejects an output
    row that lacks a key the `outputs` list declares.
12. Run `yarn pd4castr test`.

The model stops with an error in these cases, among others:

- The input holds more intervals than `PRICE_TABLE_CAPACITY`:
  `<count> intervals for <region> exceed the workbook's price table capacity of <capacity> rows`.
  The number of predispatch intervals depends on the time of day, so leave spare
  rows in the price table.
- An output row's first column doesn't match the `DATETIME` in the same row of
  the price table:
  `Outputs!<cell> is <value>, expected <datetime>; LibreOffice did not recalculate or the Outputs sheet does not line up with the price table`.
- An output cell doesn't hold a number:
  `Outputs!<cell> is <value>, expected a number; LibreOffice did not calculate the workbook`.
- The output row after the last interval isn't empty:
  `Outputs sheet has more rows than the <count> intervals in the price table`.

The scripts in `scripts/` hardcode the sample workbook's layout and battery
parameters. `scripts/build_workbook.py` regenerates `model/battery_plan.xlsx`.
To run it, install [uv](https://docs.astral.sh/uv/), which installs the script's
one dependency, openpyxl, and run `uv run scripts/build_workbook.py`.
`scripts/check_output.py` compares a model output with the reference plan. When
you replace the workbook, delete these scripts or write a reference check for
your own calculation.

## Workbook features that don't work

The container holds LibreOffice and the one workbook file, without Excel and
without access to your other files or data sources. These features fail there:

- **VBA macros.** The model never runs macros. Move any calculation a macro
  performs into formulas.
- **Links to other workbooks.** The linked workbooks aren't in the container, so
  a formula that reads one returns an error or a stale value. Copy the data the
  link reads into a sheet of your workbook.
- **Live data connections.** LibreOffice doesn't refresh Power Query, external
  data ranges or web queries. Declare the data as a pd4castr input instead, and
  change the model to write it into a sheet.
- **Excel functions LibreOffice 7.4 lacks.** The image installs LibreOffice 7.4,
  the version Debian 12 ships. LibreOffice 7.4 doesn't have the dynamic array
  functions, such as `FILTER`, `SORT` and `UNIQUE`, or `LET`, `LAMBDA` and
  `XLOOKUP`. Rewrite `XLOOKUP` as `INDEX` and `MATCH`, and rewrite a dynamic
  array formula as one formula per cell over a fixed-size range.
