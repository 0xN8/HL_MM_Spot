from tools.utils import setup, ws_manager_run, ws_run, time
from tools.api import post_candle_snapshot
from tools.stats import volatility
from maker import maker
from trading.futures import futures_cancel, futures_order, futures_order_query, futures_positions
from trading.spot import spot_cancel, spot_order, spot_order_query, spot_positions
from tools.config import url, coin, ws_url, test_url, ws_test_url


def main():
    # ws_run(url)
    account, address, info, exchange = setup('spot', url)
    maker(coin, address, info, exchange)
while True:
    main()
    time.sleep(60)
