# R Forecast

This example is a model for [pd4castr](https://docs.v2.pd4castr.com.au), the
platform that runs electricity price forecasting models and compares their
forecasts. The model is an R script that forecasts each region's half-hourly
price for the next day with the
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
| `model/main.R`               | The container's start script                   |
| `model/load_input_data.R`    | Downloads the input                            |
| `model/run_model.R`          | The forecasting method                         |
| `model/upload_output_data.R` | Uploads the forecast                           |
| `Dockerfile`                 | The image, with R and its packages             |
| `queries/data-fetchers/`     | The queries that fetch dispatch prices         |
| `.pd4castrrc.json`           | Model configuration                            |
| `package.json`               | Pins the pd4castr command-line interface (CLI) |

## How a run works

`.pd4castrrc.json` declares one input, `dispatch_price`, and its `fetcher` entry
lists the two queries in `queries/data-fetchers/` that pd4castr runs against
AEMO's market data. Every 5 minutes, pd4castr runs `dispatch_price_check.sql`,
which returns the latest `HH:00` or `HH:30` time that AEMO has published a
dispatch price for. When that time changes, pd4castr runs
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

pd4castr starts the model's container with two signed URLs in its environment:
`INPUT_DISPATCH_PRICE_URL` to download those rows from, and `OUTPUT_URL` to
upload the forecast to. The container runs `model/main.R`, which goes through 3
stages:

1. `load_input_data.R` downloads the input.
2. `run_model.R` forecasts each region's price for the 48 half-hours after the
   input's last half-hour.
3. `upload_output_data.R` uploads the forecast to `OUTPUT_URL` with an HTTP
   `PUT`, as a JSON array.

The forecast has one row per half-hour. Each row holds a `forecast_datetime`
column and 3 columns per region: the forecast, and the lower and upper bounds of
its 80% prediction interval. This row is shortened to one region:

```json
{
  "forecast_datetime": "2026-10-13T07:30:00Z",
  "nsw1": 121.91,
  "nsw1_lower": 109.03,
  "nsw1_upper": 134.79
}
```

Each column matches the `key` of an entry in the `outputs` list of
`.pd4castrrc.json`. The entries for the forecast columns set
`"seriesKey": true`, so the pd4castr chart draws a line for each region. The
entries for the bound columns set `"seriesKey": false`, so the chart leaves them
out, and they stay in the forecast that pd4castr stores for the run.

## The forecasting method

`run_model.R` fits a separate model to each region's prices, in 4 steps:

1. It places the prices on a complete half-hour grid and interpolates any
   half-hour missing from the input with `forecast::na.interp`.
2. It clips the prices to the region's own 1st and 99th percentiles, which
   `CLIP_QUANTILES` sets. A price spike can reach thousands of dollars per
   megawatt-hour in a single half-hour, and the clip stops one spike from
   pulling the fitted daily and weekly patterns towards it.
3. It fits `forecast::stlf` with `method = "ets"`. Seasonal and trend
   decomposition using Loess (STL) splits the prices into a daily pattern (48
   half-hours), a weekly pattern (336 half-hours) and the remainder. An
   exponential smoothing (ETS) model forecasts the remainder, and `stlf` adds
   the daily and weekly patterns back.
4. It takes the forecast and the 80% prediction interval for the next 48
   half-hours.

The script stops with an error, and uploads nothing, when a region has fewer
than 14 days of prices in the input. It also stops when a forecast value is
missing or falls outside its prediction interval.

## Resource limits

pd4castr runs each model container with a quarter of a virtual CPU (0.25 vCPU)
and 512 MiB of memory, and stops a run after 600 s. With 8 weeks of prices for 5
regions, this model runs in 9 s at those limits, and the container's memory
peaks at 255 MiB. That peak includes the files the container reads, which the
kernel keeps in memory. The R process alone peaks at about 172 MiB.

Two common methods for prices with daily and weekly patterns don't fit in those
limits:

- TBATS (`forecast::tbats`) needs more than 512 MiB on 8 weeks of prices, so the
  platform kills the container.
- `forecast::auto.arima` with Fourier terms for both patterns runs for more than
  600 s at 0.25 vCPU.

## Editing the model

To change the forecast, edit `model/run_model.R`. The constants at the top of
the file set the forecast horizon, the clip, the prediction interval and the
seasonal periods.

When you change `INTERVAL_LEVEL`, change the `80%` in the `name` of each bound
column's entry in `.pd4castrrc.json`, such as `NSW1 lower 80%`. Leave each `key`
as it is, because the columns in `run_model.R` keep their names.

`dispatch_price_fetch.sql` fetches 56 days of prices (`interval '56 days'`).
`run_model.R` needs at least 14 days for each region (`MIN_OBSERVED`), so keep
the fetch window at 14 days or more.

The columns in `run_model.R` and the `outputs` entries in `.pd4castrrc.json`
must match. pd4castr fails any run whose forecast is missing a column that
`outputs` lists. When you add or remove a column in `run_model.R`, add or remove
its entry in `outputs`.

To use another R package, add it to the `apt-get install` line in the
`Dockerfile`. The image runs Debian 12 ("bookworm"), which ships most packages
from CRAN, the R package archive, as `r-cran-<name>`. To find one, search
[packages.debian.org](https://packages.debian.org/bookworm/). A CRAN package
that Debian doesn't ship has to be compiled in the image with
`install.packages`, which needs Debian's `r-base-dev` compiler toolchain in the
`Dockerfile`.

## Testing and publishing

The commands below use the pd4castr CLI that `package.json` pins, and need
Node.js with Yarn, and Docker. The
[pd4castr documentation](https://docs.v2.pd4castr.com.au) covers logging in and
each command's options.

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

`pd4castr test` runs the container without the platform's limits. To run it at
the limits, start it with `docker run`'s limit flags. Set
`INPUT_DISPATCH_PRICE_URL` to a URL that serves a file from `test_input/`, and
`OUTPUT_URL` to a URL that accepts an HTTP `PUT`:

```bash
docker build --platform linux/amd64 -t r-forecast .
docker run --rm --platform linux/amd64 --cpus=0.25 --memory=512m --memory-swap=512m \
  -e INPUT_DISPATCH_PRICE_URL=<input_url> -e OUTPUT_URL=<output_url> r-forecast
```

## Base image

The `Dockerfile` starts from `debian:12.15-slim` and installs R and the
`forecast`, `httr` and `jsonlite` packages from Debian, which ships them
prebuilt. The build takes about 1 minute and compiles nothing. Debian 12 ships R
4.2.2 and `forecast` 8.20. The `Dockerfile` then deletes documentation,
translations, and each R package's help and tests. The image is 227 MB, or 103
MB compressed. The Rocker project's `rocker/r-ver`, a common base image for R,
is 398 MB compressed.
