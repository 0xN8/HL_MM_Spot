import requests
import json

url = "https://api.hyperliquid.xyz/info"
headers = {"Content-Type": "application/json"}

def post_candle_snapshot(coin, interval, start_time, end_time):
    body = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    return response.json()


