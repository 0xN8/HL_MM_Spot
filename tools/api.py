from tools.config import url, test_url, headers
import requests, json, time

url += "/info"
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

def post_user_spot_tokens(address):
    body = {
        "type": "spotClearinghouseState",
        "user": address
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    print("User Tokens response: ", response)
    return response.json()

def post_user_orders(address):
    body = {
        "type": "openOrders",
        "user": address
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    print("User Orders response: ", response)
    return response.json()

def post_l2_book(coin):
    body = {
        "type": "l2Book",
        "coin": coin
    }

    response = requests.post(url, headers=headers, data=json.dumps(body))
    print("L2 Book response: ", response)
    return response.json()
