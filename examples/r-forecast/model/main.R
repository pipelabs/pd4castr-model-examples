# Downloads the dispatch_price input, forecasts each region's price for the
# next day, and uploads the forecast to OUTPUT_URL.

source("model/load_input_data.R")
source("model/run_model.R")
source("model/upload_output_data.R")

require_env <- function(name) {
  value <- Sys.getenv(name)

  if (!nzchar(value)) {
    stop(name, " is not set", call. = FALSE)
  }

  value
}

input_url <- require_env("INPUT_DISPATCH_PRICE_URL")
output_url <- require_env("OUTPUT_URL")

prices <- load_dispatch_prices(input_url)
output <- build_forecast(prices)
send_output(output, output_url)

message("Done")
