REGIONS <- c("NSW1", "QLD1", "SA1", "TAS1", "VIC1")

HALF_HOUR_SECONDS <- 30 * 60

# The forecast covers the 48 half-hours (one day) after the input's last
# half-hour.
HORIZON <- 48

# Prices repeat daily (48 half-hours) and weekly (336 half-hours).
SEASONAL_PERIODS <- c(48, 336)

# STL drops the weekly period from a series shorter than 2 weeks plus one
# half-hour, so the model needs 3 weeks of observed prices.
MIN_OBSERVED <- 3 * 336

# Each region's prices are clipped to its own 1st and 99th percentiles before
# fitting, so a few extreme intervals don't dominate the fit.
CLIP_QUANTILES <- c(0.01, 0.99)

# The forecast's prediction interval, in percent.
INTERVAL_LEVEL <- 80

build_forecast <- function(prices) {
  last_time <- max(prices$time)
  grid <- seq(min(prices$time), last_time, by = HALF_HOUR_SECONDS)
  forecast_times <- last_time + HALF_HOUR_SECONDS * seq_len(HORIZON)

  output <- data.frame(
    forecast_datetime = format(forecast_times, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
  )

  for (region in REGIONS) {
    message("Fitting ", region, "...")

    history <- build_region_history(prices, region, grid)
    fit <- forecast::stlf(
      history,
      h = HORIZON,
      method = "ets",
      level = INTERVAL_LEVEL
    )

    key <- tolower(region)
    output[[key]] <- round(as.numeric(fit$mean), 2)
    output[[paste0(key, "_lower")]] <- round(as.numeric(fit$lower), 2)
    output[[paste0(key, "_upper")]] <- round(as.numeric(fit$upper), 2)
  }

  require_valid_forecast(output)

  output
}

# One region's prices on the complete half-hour grid, clipped, with any
# missing half-hours interpolated.
build_region_history <- function(prices, region, grid) {
  region_prices <- prices[prices$region == region, ]
  observed <- region_prices$price[match(grid, region_prices$time)]

  if (sum(!is.na(observed)) < MIN_OBSERVED) {
    stop(
      "The dispatch_price input has ", sum(!is.na(observed)), " half-hours for ",
      region, ", fewer than the ", MIN_OBSERVED, " the model needs",
      call. = FALSE
    )
  }

  limits <- stats::quantile(observed, CLIP_QUANTILES, na.rm = TRUE)
  clipped <- pmin(pmax(observed, limits[[1]]), limits[[2]])

  forecast::na.interp(
    forecast::msts(clipped, seasonal.periods = SEASONAL_PERIODS)
  )
}

require_valid_forecast <- function(output) {
  values <- output[names(output) != "forecast_datetime"]

  if (!all(vapply(values, function(column) all(is.finite(column)), logical(1)))) {
    stop("The forecast has a missing or non-finite value", call. = FALSE)
  }

  for (key in tolower(REGIONS)) {
    lower <- output[[paste0(key, "_lower")]]
    upper <- output[[paste0(key, "_upper")]]

    if (any(lower > output[[key]] | output[[key]] > upper)) {
      stop("The ", key, " forecast falls outside its interval", call. = FALSE)
    }
  }
}
