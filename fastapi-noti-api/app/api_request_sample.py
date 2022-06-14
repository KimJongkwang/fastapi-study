import base64
import hmac
from datetime import datetime, timedelta
import requests


def parse_params_to_str(params):
    url = "?"
    for key, value in params.items():
        url = url + str(key) + "=" + str(value) + "&"
    return url[1:-1]


def hash_string(qs, secret_key):
    mac = hmac.new(bytes(secret_key, encoding="utf8"), bytes(qs, encoding="utf8"), digestmod="sha256")
    d = mac.digest()
    validating_secret = str(base64.b64encode(d).decode("utf-8"))
    return validating_secret


def sample_request():
    access_key = "6d8ac3b0-a08f-4fcc-a1b6-319bd0bb-5239-4875-8fdf-be63af1a8d28"
    secret_key = "0SRtSm0ZcGQvSibZ5kGWdtxx4ZipABJFsJjOveFu"
    cur_time = datetime.utcnow() + timedelta(hours=9)
    cur_timestamp = int(cur_time.timestamp())
    qs = dict(key=access_key, timestamp=cur_timestamp)
    header_secret = hash_string(parse_params_to_str(qs), secret_key)

    url = f"http://127.0.0.1:80/api/services?{parse_params_to_str(qs)}"
    res = requests.get(url, headers=dict(secret=header_secret))
    return res


print(sample_request().json())
