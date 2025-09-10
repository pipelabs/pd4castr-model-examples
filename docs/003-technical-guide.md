# Technical Guide

_Last Updated: 10th Sept. '25_

- [Overview](#overview)
- [Model Container - Input Data](#model-container---input-data)
- [Model Container - Output Data](#model-container---output-data)
- [Model Input Triggers](#model-input-triggers)
- [Model Output Format](#model-output-format)

## Overview

At a high level, a pd4castr model is a docker image and accompanying
configuration that defines input and output data.

The pd4castr platform then runs this image in a docker container in response to
your configured input [triggers](#model-input-triggers), and provides the
expected [input data](#model-container---input-data) to the container along with
a URL that receives [output data](#model-container---output-data) in the
expected [output format](#model-output-format).

## Model Container - Input Data

Input data is not directly provided to the container, but instead is provided
via a URL passed as an environment variable which can be fetched via a standard
HTTP GET request.

These URLs map to the latest file found in the input source for the specific
input.

For example, this input configuration:

```json
{
  ...
  "inputs": [{
    "key": "example_data",
    "inputSource": "0bdfd52b-efaa-455e-9a3b-1a6d2b879b73",
    ...
  }]
}
```

Will provide the latest file in the specified input source for this specific
input at a URL exposed via the `INPUT_EXAMPLE_DATA_URL` variable.

## Model Container - Output Data

A model container is provided an `OUTPUT_URL` environment variable which
provides a URL where output can be uploaded to via a standard HTTP PUT request.

## Model Input Triggers

When you configure a model input, you are required to choose a trigger type.
This determines how the input will be evaluated when the platform decides wether
to run the model. This value can be either:

- `USE_MOST_RECENT_FILE` - the condition will evaluate true if there is any
  input data at all
- `WAIT_FOR_LATEST_FILE` - the condition will evaluate true only when new data
  is available since the previous model run

When all configured model inputs have their trigger condition evaluate to true,
the model will be ran by the platform. This will be reevaluated whenever new
input data is made available, either manually uploaded by the user, or
automatically by a data fetcher.

## Model Output Format

When uploading output data it is important that each output record matches your
output configuration, and includes a required `forecast_datetime` property that
ties each record to an
[ISO 8601 timestamp](https://en.wikipedia.org/wiki/ISO_8601).

For example, if your output configuration looks like:

```json
{
  "outputs": [
    {
      "name": "VAR1",
      "type": "float",
      "seriesKey": true
    }
  ]
}
```

Then your output data should look like:

```json
[
  {
    "VAR1": 1148.5494,
    "forecast_datetime": "2025-07-13T08:00:00.000"
  },
  {
    "VAR1": 983.1223,
    "forecast_datetime": "2025-07-14T08:00:00.000"
  }
]
```
