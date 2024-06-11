from hyperliquid.utils import constants
from utils import setup
from maker import trade
from hyperliquid.websocket_manager import WebsocketManager


def sub_msg(msg):
    print("Received message: ", msg)

def main():
    url = 'https://api.hyperliquid.xyz'
    coin = "PURR/USDC"
    subscription = {"type": "allMids"}

    ws_manager = WebsocketManager(url)
    ws_manager.start()

    # ws_manager.start()
    ws_manager.subscribe(subscription, sub_msg)

    
    print("Connecting to websocket...", ws_manager)
    # account, address, info, exchange = setup('spot', url)

    # order_id = futures_order(exchange)
    # futures_cancel(order_id, exchange)

    # order_id = spot_order(exchange, coin)
    # spot_cancel(order_id, exchange, coin)
    # trade()

main()