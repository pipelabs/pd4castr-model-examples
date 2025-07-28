import os
import requests

def load_input_data():
    """
    Load input data from environment variables and download from URLs.

    Returns:
        tuple: (pd_price_json, pd_regionsum_json, dp_json) - the input data from each input source
    """

    # Read the input data URLs from environment variables.
    # Note the format here - INPUT_<INPUT_SOURCE_NAME>_URL
    pd_price_url = os.getenv('INPUT_PREDISPATCH_PRICE_URL')
    pd_regionsum_url = os.getenv('INPUT_PREDISPATCH_REGION_SUM_URL')
    dp_url = os.getenv('INPUT_DISPATCH_PRICE_URL')

    # If any of the input URLs are missing, raise an error.
    if not all([pd_price_url, pd_regionsum_url, dp_url]):
        raise ValueError("Missing required input URLs in environment variables")

    # Download input data from the input source URLs.
    print("Downloading predispatch price data...")
    pd_price_json = requests.get(pd_price_url).json()

    print("Downloading predispatch region sum data...")
    pd_regionsum_json = requests.get(pd_regionsum_url).json()

    print("Downloading dispatch price data...")
    dp_json = requests.get(dp_url).json()

    print("Successfully loaded all input data")
    return pd_price_json, pd_regionsum_json, dp_json
