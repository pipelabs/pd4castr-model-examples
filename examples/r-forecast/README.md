# R Forecast

This example is a model for [pd4castr](https://docs.v2.pd4castr.com.au), the
platform that runs electricity price forecasting models and compares their
forecasts. The model is an R script that forecasts each region's half-hourly
price for the next 24 hours with the
[`forecast`](https://pkg.robjhyndman.com/forecast/) package, and gives each
forecast an 80% prediction interval. Start from this example to package an R
model for pd4castr.

The model covers the 5 regions of the National Electricity Market (NEM): `NSW1`,
`QLD1`, `SA1`, `TAS1` and `VIC1`. The Australian Energy Market Operator (AEMO)
sets a dispatch price for each region every 5 minutes, and the model forecasts
the average dispatch price of each half-hour. It learns each region's daily and
weekly price pattern from the last 8 weeks of prices and projects it 48
half-hours ahead.

## Project layout

| Path                         | Contents                                       |
| ---------------------------- | ---------------------------------------------- |
| `model/main.R`               | The script the Docker image runs               |
| `model/load_input_data.R`    | Downloads the input                            |
| `model/run_model.R`          | The forecasting method                         |
| `model/upload_output_data.R` | Uploads the forecast                           |
| `Dockerfile`                 | The image, with R and its packages             |
| `queries/data-fetchers/`     | The queries that fetch dispatch prices         |
| `.pd4castrrc.json`           | Model configuration                            |
| `package.json`               | Pins the pd4castr command-line interface (CLI) |

## How a run works

A run has 3 parts: pd4castr fetches the input, the model's container forecasts
from it, and the container uploads the forecast.

`.pd4castrrc.json` declares one input, `dispatch_price`, and its `fetcher` entry
lists the two queries in `queries/data-fetchers/` that pd4castr runs against
AEMO's market data. Every 5 minutes, pd4castr runs `dispatch_price_check.sql`,
which returns the latest half-hour boundary (`HH:00` or `HH:30`) that has a
published dispatch price. When that time changes, pd4castr runs
`dispatch_price_fetch.sql` and starts a model run, so the model runs every 30
minutes.

`dispatch_price_fetch.sql` returns the average dispatch price of each half-hour
in the last 8 weeks, one row per half-hour and region. `SETTLEMENTDATE` is the
time the half-hour ends:

```json
{
  "SETTLEMENTDATE": "2026-10-13T07:00:00.000Z",
  "REGIONID": "NSW1",
  "RRP": 84.12
}
```

pd4castr then starts the model's container with two URLs in its environment,
each a temporary link to one file: `INPUT_DISPATCH_PRICE_URL` to download those
rows from, and `OUTPUT_URL` to upload the forecast to. The container runs
`model/main.R`, which goes through 3 stages:

1. `load_input_data.R` downloads the input.
2. `run_model.R` forecasts each region's price for the 48 half-hours after the
   input's last half-hour.
3. `upload_output_data.R` uploads the forecast to `OUTPUT_URL` with an HTTP
   `PUT`, as a JSON array.

The forecast has one row per half-hour, and `forecast_datetime` is the time the
half-hour ends. Each row also holds 3 columns per region: the forecast, and the
lower and upper bounds of its 80% prediction interval. This row is shortened to
one region:

```json
{
  "forecast_datetime": "2026-10-13T07:30:00Z",
  "nsw1": 121.91,
  "nsw1_lower": 109.03,
  "nsw1_upper": 134.79
}
```

Each column matches the `key` of an entry in the `outputs` list of
`.pd4castrrc.json`. An entry's `seriesKey` sets whether the forecast chart in
the pd4castr app draws the column as a line. The entries for the point forecast
columns, such as `nsw1`, set `"seriesKey": true`, so the chart draws a line for
each region. The entries for the bound columns set `"seriesKey": false`.
pd4castr stores the bound columns with the run even though the chart leaves them
out.

## The forecasting method

`run_model.R` forecasts each region separately, in 4 steps:

1. It clips the region's prices to their own 1st and 99th percentiles. A price
   spike can reach thousands of dollars per megawatt-hour in a single half-hour,
   and the clip stops one spike from pulling the fitted daily and weekly
   patterns towards it. The `CLIP_QUANTILES` constant sets the percentiles.
2. It places the clipped prices on a complete half-hour grid and interpolates
   any half-hour missing from the input with `forecast::na.interp`.
3. It fits `forecast::stlf` with `method = "ets"`. STL, a seasonal and trend
   decomposition that uses local regression, splits the prices into a daily
   pattern, a weekly pattern, and a seasonally adjusted series that holds the
   trend and the remainder. The daily pattern repeats every 48 half-hours and
   the weekly pattern every 336. An exponential smoothing (ETS) model forecasts
   the seasonally adjusted series, and `stlf` adds the daily and weekly patterns
   back.
4. It takes the point forecast and the 80% prediction interval for the next 48
   half-hours.

`run_model.R` stops with an error when a region has fewer than 3 weeks of prices
in the input. It also stops when any value in the forecast is missing or
infinite, or when a point forecast falls outside its prediction interval, so a
broken fit never reaches pd4castr. In both cases `main.R` uploads nothing and
the run fails.

## Resource limits

pd4castr runs each model container with a quarter of a virtual CPU (0.25 vCPU)
and 512 MiB of memory, and stops a run after 600 s. With 8 weeks of prices for 5
regions, this model runs in 9 s at those limits, and the container's memory
peaks at 255 MiB. That peak includes the files the container reads, which the
kernel keeps in memory. The R process alone peaks at about 172 MiB.

Two methods that model daily and weekly patterns don't fit in those limits:

- TBATS (`forecast::tbats`) needs more than 512 MiB on 8 weeks of prices, so
  pd4castr stops the container.
- `forecast::auto.arima` with Fourier terms for both patterns runs for more than
  600 s at 0.25 vCPU.

## Editing the model

The constants at the top of `model/run_model.R` set the forecast horizon, the
clip, the prediction interval and the seasonal periods. Changes to the
prediction interval, the fetch window, the forecast's columns or the R packages
also touch other files.

When you change `INTERVAL_LEVEL`, change the `80%` in the `name` of each bound
column's entry in `.pd4castrrc.json`, such as `NSW1 lower 80%`. Leave each `key`
as it is, because the column names in `run_model.R` don't include the level.

The fetch window is the 8 weeks of prices that `dispatch_price_fetch.sql`
returns (`interval '56 days'`). With exactly 2 weeks of prices, STL drops the
weekly pattern, so `run_model.R` needs at least 3 weeks for each region.
`MIN_OBSERVED` holds that minimum, in half-hours. Keep the fetch window at 3
weeks or more.

pd4castr fails any run whose forecast is missing a column that the `outputs`
list in `.pd4castrrc.json` holds. When you add or remove a column in
`run_model.R`, add or remove its entry in `outputs`.

To use another R package, add its Debian package name to the `apt-get install`
line in the `Dockerfile`. The image runs Debian 12 ("bookworm"), which ships
packages from CRAN, the R package archive, as `r-cran-<name>`. To check whether
Debian ships the package you need, search
[packages.debian.org](https://packages.debian.org/bookworm/). To use a CRAN
package that Debian doesn't ship, add `r-base-dev` to the `apt-get install`
line, and install the package in a `RUN Rscript -e 'install.packages("<name>")'`
step, which compiles it during the build.

## Testing and publishing

The commands below need Node.js, Yarn and Docker. They use the pd4castr CLI that
`package.json` pins, and the
[pd4castr documentation](https://docs.v2.pd4castr.com.au) covers each command's
options.

1. Install the CLI:

   ```bash
   yarn install
   ```

2. Log in to pd4castr:

   ```bash
   yarn pd4castr login
   ```

3. Fetch recent prices into `test_input/`:

   ```bash
   yarn pd4castr fetch
   ```

4. Build the image and run the model against `test_input/`:

   ```bash
   yarn pd4castr test
   ```

   Expect `Model output validation passed`. The CLI writes the forecast to
   `test_output/`.

5. Publish the model:

   ```bash
   yarn pd4castr publish
   ```

## Base image

The `Dockerfile` starts from `debian:12.15-slim` and installs R and the
`forecast`, `httr` and `jsonlite` packages from Debian, which ships them
prebuilt. The build takes about 1 minute and compiles nothing. After the
install, the `Dockerfile` deletes documentation, translations, and each R
package's help and tests. Debian 12 ships R 4.2.2 and `forecast` 8.20. The image
is 227 MB, or 103 MB compressed.
