NEM_OFFSET_SECONDS <- 10 * 60 * 60

# Downloads the dispatch_price input: one row per half-hour and region, with
# SETTLEMENTDATE marking the end of the half-hour.
load_dispatch_prices <- function(url) {
  message("Downloading dispatch_price input...")

  response <- httr::GET(url, httr::timeout(60))
  httr::stop_for_status(response, task = "download the dispatch_price input")

  rows <- jsonlite::fromJSON(
    httr::content(response, as = "text", encoding = "UTF-8")
  )

  if (length(rows) == 0 || nrow(rows) == 0) {
    stop("The dispatch_price input has no rows", call. = FALSE)
  }

  prices <- data.frame(
    # The input is in NEM time, which is UTC+10 all year:
    # "2026-10-13T17:00:00.000+10:00" -> 2026-10-13 07:00:00 UTC
    time = as.POSIXct(
      substr(rows$SETTLEMENTDATE, 1, 19),
      format = "%Y-%m-%dT%H:%M:%S",
      tz = "UTC"
    ) - NEM_OFFSET_SECONDS,
    region = rows$REGIONID,
    price = as.numeric(rows$RRP)
  )

  if (anyNA(prices$time)) {
    stop("The dispatch_price input has an unreadable SETTLEMENTDATE", call. = FALSE)
  }

  message("Read ", nrow(prices), " prices")

  prices
}
