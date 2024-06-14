import requests, json, time, os
from dotenv import load_dotenv


url = "https://api.hyperliquid.xyz/info"
headers = {"Content-Type": "application/json"}
minute_ms = 60000
candle_spread = 500



def post_candle_snapshot(coin, interval_str, interval_int):

    time_diff = minute_ms * candle_spread * interval_int
    end_time = int(time.time() * 1000)
    start_time = end_time - time_diff

    body = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": interval_str,
            "startTime": start_time,
            "endTime": end_time
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    print("Candle Snapshot response: ", response)
    return response.json()

def post_user_tokens():
    load_dotenv()
    body = {
        "type": "spotClearinghouseState",
        "user": os.getenv('wallet_address')
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    print("User Tokens response: ", response)
    return response.json()
