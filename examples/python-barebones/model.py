"""Barebones pd4castr model template.

Fill in `run_model` with your forecasting logic and publish with `pd4castr
publish`. Configure inputs and outputs in `.pd4castrrc.json` — see
https://docs.v2.pd4castr.com.au/authoring for the full reference.

Inputs are exposed to the container as `INPUT_<KEY>_URL` environment variables;
fetch them with HTTP GET. The output URL is exposed as `OUTPUT_URL` and expects
an HTTP PUT of your forecast as JSON.
"""

import json
import os

import requests


def run_model() -> list[dict]:
    # TODO: replace with your forecasting logic. Return one dict per output row.
    return []


def upload_output(results: list[dict]) -> None:
    output_url = os.environ["OUTPUT_URL"]

    response = requests.put(
        output_url,
        data=json.dumps(results),
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()


if __name__ == "__main__":
    print("Running model...")
    results = run_model()
    print(f"Generated {len(results)} output rows")

    upload_output(results)
    print("Done")
