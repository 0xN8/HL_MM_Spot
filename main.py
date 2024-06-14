from utils import setup, ws_manager_run, ws_run
from api import post_candle_snapshot
from stats import volatility
from maker import maker
from futures import futures_cancel, futures_order, futures_order_query, futures_positions
from spot import spot_cancel, spot_order, spot_order_query, spot_positions

url = 'wss://api.hyperliquid-testnet.xyz/ws'
coin = "PURR/USDC"


def main():
    # ws_run(url)
    # account, address, info, exchange = setup('spot', url)
    maker(coin)
    # order_id = futures_order(exchange)
    # futures_cancel(order_id, exchange)

    # order_id = spot_order(exchange, coin)
    # spot_cancel(order_id, exchange, coin)
    # trade()

main()