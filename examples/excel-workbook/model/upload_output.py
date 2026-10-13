import json

import requests

from env import get_required_env


def send_output(rows: list[dict]) -> None:
    url = get_required_env("OUTPUT_URL")
    response = requests.put(
        url,
        data=json.dumps(rows),
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    if not response.ok:
        raise RuntimeError(
            f"Output upload failed: HTTP {response.status_code}: {response.text[:2000]}"
        )
    print(f"Uploaded {len(rows)} output rows")
