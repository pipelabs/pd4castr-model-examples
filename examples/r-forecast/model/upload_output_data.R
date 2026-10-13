# Uploads the forecast as a JSON array with one object per half-hour.
send_output <- function(output, url) {
  message("Uploading ", nrow(output), " rows...")

  body <- jsonlite::toJSON(output, dataframe = "rows", digits = NA)
  response <- httr::PUT(url, body = body, httr::content_type_json())
  httr::stop_for_status(response, task = "upload the output")
}
