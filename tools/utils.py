from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from hyperliquid.websocket_manager import WebsocketManager
from dotenv import load_dotenv
import os, eth_account, json, time, threading, websocket



def setup(url):
    load_dotenv()
    priv_key = os.getenv('api_priv_key')
    account: LocalAccount = eth_account.Account.from_key(priv_key)
    address = os.getenv('wallet_address')
    info = Info(url, skip_ws= False)
    exchange = Exchange(account, url, account_address=account.address)


    # Set address to the api address if no wallet is provided
    if address == "":
        address = account.address

    return account, address, info, exchange

def on_open(ws):
    print("WebSocket connection opened.")
    # Send a message to the server after the connection is opened.
    # Replace this with the actual message you want to send.
    subscription = json.dumps({"method":"subscribe", "subscription":{"type": "candle", "coin": "ETH", "interval":"1m"}})
    ws.send(subscription)

def on_message(ws, message):
    print("Received message: ", message)

def manager_on_msg(message):
    print("Received message: ", message)

def on_error(ws, error):
    print("Error: ", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed.: ", close_status_code, close_msg)

def send_ping(ws):
    while True:
        time.sleep(50)
        ws.send(json.dumps({"method":"ping"}))


def ws_run(url):
    ws = websocket.WebSocketApp(url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    print(ws)
    ping_thread = threading.Thread(target=send_ping, args=(ws,))
    ping_thread.start()
    ws.run_forever()   

def ws_manager_run(url, subscription):
    ws_manager = WebsocketManager(url)
    ws_manager.start()
    ws_manager.subscribe(subscription, manager_on_msg)



def elapsed_time():
    while True:
        start_time = time.time() * 1000
        elapsed_time = time.time()*1000 - start_time

        print(f"Elapsed time: {elapsed_time} ms")