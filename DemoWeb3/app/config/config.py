import json
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent


def get_secrets(
    key: str,
    default_value: Optional[str] = None,
    json_path=str(BASE_DIR / "secrets.json"),
):
    with open(json_path, "r") as f:
        secrets = json.load(f)

    try:
        return secrets[key]
    except KeyError:
        if default_value:
            return default_value
        raise EnvironmentError(f"Set the Json key({key}) in secrets.json")
