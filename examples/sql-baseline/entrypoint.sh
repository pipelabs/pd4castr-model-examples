#!/bin/sh
# Downloads the input, runs model.sql with DuckDB, and uploads the output.
set -eu

: "${INPUT_DISPATCH_PRICE_URL:?INPUT_DISPATCH_PRICE_URL is not set}"
: "${OUTPUT_URL:?OUTPUT_URL is not set}"

workdir=$(mktemp -d)
cd "$workdir"

echo "Downloading dispatch_price input..."
curl -fsS --retry 3 -o dispatch_price.json "$INPUT_DISPATCH_PRICE_URL"

echo "Running model.sql..."
duckdb < /app/model.sql

echo "Uploading output..."
curl -fsS --retry 3 -o /dev/null -X PUT \
  -H 'Content-Type: application/json' \
  --data-binary @output.json \
  "$OUTPUT_URL"

echo "Done"
