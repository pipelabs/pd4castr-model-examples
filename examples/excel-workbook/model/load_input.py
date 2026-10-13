import requests

from env import get_required_env


def load_price_rows() -> list[dict]:
    url = get_required_env("INPUT_PREDISPATCH_PRICE_URL")
    response = requests.get(url, timeout=60)
    if not response.ok:
        raise RuntimeError(
            f"Input download failed: HTTP {response.status_code}: {response.text[:2000]}"
        )

    rows = response.json()
    if not isinstance(rows, list):
        raise ValueError("Input predispatch_price must be a JSON array")

    print(f"Loaded {len(rows)} predispatch price rows")
    return rows
