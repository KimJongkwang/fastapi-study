import requests
import json
from datetime import datetime
import time

def test_post(url):
    now_time = {'nowtime': datetime.now().strftime('%Y-%m-%d %H:%M')}
    res = requests.post(url, data=json.dumps(now_time))
    print(res.text)

def test_get(url2):
    url2 = url2 + "/date?time=now"
    res = requests.get(url2)
    print(res.text)

if __name__=="__main__":
    url = "http://localhost:8000/nowTime"

    cnt = 0
    while cnt < 10:
        test_post(url)
        test_get(url)
        cnt += 1
        time.sleep(10)
