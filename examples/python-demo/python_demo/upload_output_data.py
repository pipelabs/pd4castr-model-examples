import os
import requests
import json


def upload_output_data(results):
    """
    Upload output data to the specified URL.

    Args:
        results: List of dictionaries containing forecast data
    """
    print("Preparing output...")

    # Get the output URL from the environment variable.
    output_url = os.getenv('OUTPUT_URL')
    if not output_url:
        raise ValueError("Missing OUTPUT_URL environment variable")

    # Convert the results to a JSON object.
    print(f"Converting output with {len(results)} data points to JSON")
    output_json = json.dumps(results)
    print(f"Generated JSON output of length {len(output_json)} characters")

    # Upload the JSON object to the output URL
    print(f"Uploading results to {output_url}")
    try:
        response = requests.put(output_url, data=output_json, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        print("Successfully uploaded results")
    except requests.exceptions.RequestException as e:
        print(f"Error uploading results: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise
