# SQL Baseline

This example is a model for [pd4castr](https://docs.v2.pd4castr.com.au), the platform that runs electricity price forecasting models and compares their forecasts. The model's whole forecasting logic is one SQL file, [`model.sql`](./model.sql), which the [DuckDB](https://duckdb.org) command-line tool runs. Start from this example to write a model in SQL, or publish it to pd4castr as a baseline to measure other models against.

The model forecasts the spot price in the 5 regions of the National Electricity Market (NEM): `NSW1`, `QLD1`, `SA1`, `TAS1` and `VIC1`. The Australian Energy Market Operator (AEMO) sets a dispatch price for each region every 5 minutes. For each half-hour and region, this model forecasts the dispatch price from the same time one week earlier, a method called a seasonal-naive forecast. A model that can't forecast more accurately than this baseline does no better than repeating last week's prices.

## Project layout

| Path | Contents |
| --- | --- |
| `model.sql` | The model |
| `entrypoint.sh` | The container's start script |
| `Dockerfile` | Alpine image with curl and a pinned DuckDB release |
| `queries/data-fetchers/` | The queries that fetch dispatch prices from AEMO's market data |
| `.pd4castrrc.json` | Model configuration |
| `package.json` | Pins the pd4castr command-line interface (CLI) |

## How a run works

This section follows one model run, from the input pd4castr fetches to the forecast the model uploads.

pd4castr builds the input with the two queries in `queries/data-fetchers/`, which `.pd4castrrc.json` lists under the input's `fetcher`. Every 5 minutes, pd4castr runs `dispatch_price_check.sql`, which returns the latest `HH:00` or `HH:30` time that AEMO has published a dispatch price for. When that time changes, pd4castr runs `dispatch_price_fetch.sql` and starts a model run, so the model runs every 30 minutes.

The input holds every dispatch price from the last 7 days, one row per 5-minute interval and region. `SETTLEMENTDATE` is the time the interval ends, in NEM time (UTC+10 all year), and `RRP` is the price in $/MWh:

```json
{ "SETTLEMENTDATE": "2026-10-13T17:00:00.000+10:00", "REGIONID": "NSW1", "RRP": "84.12000" }
```

pd4castr starts the model's container with two signed URLs in its environment: `INPUT_DISPATCH_PRICE_URL` to download the input from, and `OUTPUT_URL` to upload the forecast to. The container goes through 3 stages:

1. `entrypoint.sh` creates a working directory and downloads the input into it as `dispatch_price.json`.
2. DuckDB runs `model.sql` in the working directory, and `model.sql` writes `output.json` there.
3. `entrypoint.sh` uploads `output.json` to `OUTPUT_URL` with an HTTP `PUT`.

`model.sql` uses the price of the 5-minute interval that ends at each `HH:00` and `HH:30` as the price for the half-hour ending then. It finds the latest of those times in the input and forecasts the 48 half-hours after it. The output has one row per half-hour, with a `forecast_datetime` column in UTC and one column per region. The row for 17:30 NEM time is:

```json
{ "forecast_datetime": "2026-10-13T07:30:00Z", "nsw1": 91.5, "qld1": 88.02, "sa1": 102.3, "tas1": 67.8, "vic1": 95.11 }
```

Each region column matches an output `key` in `.pd4castrrc.json`. When the input has no price for a region at a half-hour, that region's value in the forecast row is `null`, and when it has no price for any region, the forecast skips that half-hour.

## Editing the model

To change the forecast, edit `model.sql`. `model.sql` is a single `COPY` statement whose `WITH` clause defines 3 named queries: `dispatch_price` reads the input, `half_hourly_price` picks one price per half-hour, and `latest` finds the latest half-hour.

To forecast from yesterday's prices instead of last week's, change the lag on the `SET VARIABLE` line at the top of `model.sql`:

```sql
SET VARIABLE lag = INTERVAL 1 DAY;
```

The input covers 7 days, so a lag longer than 7 days needs a wider window in `dispatch_price_fetch.sql`.

To forecast each half-hour's average price, replace the `half_hourly_price` query with one that averages the 6 intervals ending at `HH:05` to `HH:30`, or at `HH:35` to `HH:00`:

```sql
half_hourly_price AS (
    SELECT
        time_bucket(INTERVAL 30 MINUTE, settlementdate - INTERVAL 5 MINUTE)
        + INTERVAL 30 MINUTE AS settlementdate,
        region,
        avg(price) AS price
    FROM dispatch_price
    GROUP BY ALL
),
```

The averaging query also averages the input's last half-hour when AEMO hasn't published all 6 of its intervals yet. That half-hour then counts as the latest one, and the forecast starts 30 minutes later than it would with the default query.

The output columns in `model.sql` and the `outputs` entries in `.pd4castrrc.json` must match. pd4castr treats only the columns that `outputs` lists as forecast series, and fails any run whose output is missing one of them. When you add or remove a column in `model.sql`, add or remove its entry in `outputs`.

## Testing and publishing

The commands below use the pd4castr CLI that `package.json` pins. The [pd4castr documentation](https://docs.v2.pd4castr.com.au) covers logging in and each command's options.

1. Install the CLI:

   ```bash
   yarn install
   ```

2. Log in and fetch recent prices into `test_input/`:

   ```bash
   yarn pd4castr login
   yarn pd4castr fetch
   ```

3. Build the image and run the model against `test_input/`:

   ```bash
   yarn pd4castr test
   ```

   Expect `Model output validation passed`. The CLI writes the forecast to `test_output/`.

4. Publish the model:

   ```bash
   yarn pd4castr publish
   ```

## Upgrading DuckDB

The `Dockerfile` downloads the DuckDB release that `DUCKDB_VERSION` sets, and checks the download against a SHA-256 checksum for each CPU architecture (`amd64` and `arm64`). To upgrade, change `DUCKDB_VERSION`, then replace both checksums with the digests of the `duckdb_cli-linux-amd64-musl.gz` and `duckdb_cli-linux-arm64-musl.gz` assets on the new release's page in [DuckDB's GitHub releases](https://github.com/duckdb/duckdb/releases).
