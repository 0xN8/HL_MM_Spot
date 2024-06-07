from hyperliquid.utils import constants
from utils import setup
from spot import spot_cancel, spot_order, spot_order_query, spot_positions
from futures import futures_cancel, futures_order, futures_order_query, futures_positions
from api import post_candle_snapshot

#while True:
#high = bid
#low = ask

#if curr_bid_amount() < curr_ask_amount():
#   submit bid order
#if curr_ask_amount() < curr_bid_amount():
#   submit ask order
#if inv() > x:
# bid lower
#if inv() < x:
# ask higher


def main():
    # url = constants.TESTNET_API_URL
    # coin = "PURR/USDC"
    # account, address, info, exchange = setup('futures', url)

    # order_id = futures_order(exchange)
    # futures_cancel(order_id, exchange)

    # order_id = spot_order(exchange, coin)
    # spot_cancel(order_id, exchange, coin)

    response = post_candle_snapshot("PURR/USDC","1m", 1717798210000, 1717798510000)
    last_min = response[len(response)-1]
    print(last_min)

main()