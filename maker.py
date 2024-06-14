from api import post_candle_snapshot, post_user_tokens
from stats import volatility
import numpy as np


theta = 60
gamma = 0.2 #0.1 to ~ 1
alpha = 2   #0.5 to 5


def maker(coin):
    
    #candle snapshot expects 3 params coin, interval str, interval int (measured in min)
    #ex: interval str = "1h", interval int = 60; str = "4h", int = 240
    candle_res = post_candle_snapshot(coin, "1m", 1)
    spot_res = post_user_tokens()

    close_prices = [candle['c'] for candle in candle_res]
    close_prices = list(map(float, close_prices))
    close_prices, mid_price = close_prices[:-1], close_prices[-1]

    print("Mid-price: ", mid_price)
    vol = volatility(close_prices)
    print("Volatility: ", vol)

    coin_short = coin.replace("/USDC", "")
    balances = spot_res['balances']
    print("Spot Res: ", spot_res)
    coin_inv = float(next((balance['total'] for balance in balances if balance['coin'] == coin_short), None))
    stable_inv = float(next((balance['total'] for balance in balances if balance['coin'] == "USDC"), None))
    print("Inventory: ", coin_inv)
    print("Cash: ", stable_inv)

    #HJB equation implementation of bid-ask spread
    bid = round(mid_price - (1/gamma)*np.log(1+(gamma*(vol*vol)*theta*(alpha - coin_inv))),5)
    ask = round(mid_price + (1/gamma)*np.log(1+(gamma*(vol*vol)*theta*(alpha - coin_inv))),5)

    print("Bid: ", bid)
    print("Ask: ", ask)
    


    