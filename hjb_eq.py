from tools.api import post_candle_snapshot, post_user_spot_tokens, post_user_orders
from tools.stats import volatility
import numpy as np
from trading.spot import spot_order, spot_cancel
from termcolor import colored, cprint
import math


theta = 60 #unit: s
gamma_one = 0.15 #0.01 to 0.05, 0.1 to 0.5, 1 
alpha_one = 1.8  #0.5, 1 to 2,3 to 5

gamma_two = 0.4
alpha_two = 3.5

gamma_three = 1
alpha_three = 5


def hjb(coin, address, info, exchange):
    
    #candle snapshot expects 3 params coin, interval str, interval int (measured in min)
    #ex: interval str = "1h", interval int = 60; str = "4h", int = 240
    candle_res = post_candle_snapshot(coin, "1m", 1)
    spot_res = post_user_tokens(address)

    close_prices = [candle['c'] for candle in candle_res]
    close_prices = list(map(float, close_prices))
    close_prices, mid_price = close_prices[:-1], close_prices[-1]

    
    vol = volatility(close_prices)
    print("Volatility: ", vol)

    coin_short = coin.replace("/USDC", "")
    balances = spot_res['balances']
    coin_inv = float(next((balance['total'] for balance in balances if balance['coin'] == coin_short), None))
    stable_inv = float(next((balance['total'] for balance in balances if balance['coin'] == "USDC"), None))
    print(colored("Inventory: ",'white'), colored(coin_inv,'white'))
    print(colored("Cash: ", 'white'), colored(stable_inv,'white'))

    #HJB equations implementation of bid-ask spread with a step-wise order execution
    bid_one = round(mid_price - (1/gamma_one)*np.log(1+(gamma_one*(vol*vol)*theta*(alpha_one - 1))),5)
    ask_one = round(mid_price + (1/gamma_one)*np.log(1+(gamma_one*(vol*vol)*theta*(alpha_one + 1))),5)

    bid_two = round(mid_price - (1/gamma_two)*np.log(1+(gamma_two*(vol*vol)*theta*(alpha_two - 1))),5)
    ask_two = round(mid_price + (1/gamma_two)*np.log(1+(gamma_two*(vol*vol)*theta*(alpha_two + 1))),5)

    bid_three = round(mid_price - (1/gamma_three)*np.log(1+(gamma_three*(vol*vol)*theta*(alpha_three - 1))),5)
    ask_three = round(mid_price + (1/gamma_three)*np.log(1+(gamma_three*(vol*vol)*theta*(alpha_three + 1))),5)

    
    
    print(colored("Bid-Ask Spread 1: ", 'light_cyan'), colored(bid_one, 'cyan'), colored(ask_one, 'cyan'))
    print(colored("Bid-Ask Spread 2: ", 'light_cyan'), colored(bid_two, 'cyan'), colored(ask_two, 'cyan'))
    print(colored("Bid-Ask Spread 3: ", 'light_cyan'), colored(bid_three, 'cyan'), colored(ask_three, 'cyan'))

    print(colored("Mid-price: ",'light_blue'), colored(mid_price, 'light_blue'))
          
    user_orders = post_user_orders(address)
    print("User Open Orders: ", user_orders)

    resting_orders_bid = [False,False,False]
    resting_orders_ask = [False,False,False]
    for order in user_orders:
        order_id = order['oid']
        if order['coin'] == coin:
            if order['side'] == "B":
                if order['limitPx'] == bid_one:
                    print("Order for optimal bid_one already exists")
                    resting_orders_bid[0] = True
                    continue
                elif order['limitPx'] == bid_two:
                    print("Order for optimal bid_two already exists")
                    resting_orders_bid[1] = True
                    continue
                elif order['limitPx'] == bid_three:
                    print("Order for optimal bid_three already exists")
                    resting_orders_bid[2] = True
                    continue
                cprint(f"Cancelling optimal bid order {order_id}, Order price: {order['limitPx']}", 'light_green', 'on_red')
                spot_cancel(order_id, exchange, coin)
            elif order['side'] == "A":
                if order['limitPx'] == ask_one:
                    print("Order for optimal ask_one already exists")
                    resting_orders_ask[0] = True
                    continue
                elif order['limitPx'] == ask_two:
                    print("Order for optimal ask_two already exists")
                    resting_orders_ask[1] = True
                    continue
                elif order['limitPx'] == ask_three:
                    print("Order for optimal ask_three already exists")
                    resting_orders_ask[2] = True
                    continue
                cprint(f"Cancelling optimal ask order {order_id}, Order price: {order['limitPx']}",'light_green','on_red')
                spot_cancel(order_id, exchange, coin)

    
    if not resting_orders_bid[0] and math.floor(stable_inv) > 0:
        size = math.floor((stable_inv * 0.5)/mid_price)
        cprint(f'Placing bid order for optimal bid_one: {size}', 'light_green', 'on_blue')
        spot_order(exchange, coin, True, size, bid_one)

    if not resting_orders_bid[1] and math.floor(stable_inv) > 0:
        size = math.floor((stable_inv * 0.3)/mid_price)
        cprint(f'Placing bid order for optimal bid_two: {size}', 'light_green', 'on_blue')
        spot_order(exchange, coin, True, size, bid_two)
    
    if not resting_orders_bid[2] and math.floor(stable_inv) > 0:
        size = math.floor((stable_inv * 0.2)/mid_price)
        cprint(f'Placing bid order for optimal bid_three: {size}', 'light_green', 'on_blue')
        spot_order(exchange, coin, True, size, bid_three)
    
    if not resting_orders_ask[0] and math.floor(coin_inv) > 0:
        size = math.floor(coin_inv * 0.5)
        cprint(f'Placing ask order for optimal ask_one: {size}', 'light_green','on_magenta')
        spot_order(exchange, coin, False, size, ask_one)

    
    if not resting_orders_ask[1] and math.floor(coin_inv) > 0:
        size = math.floor(coin_inv * 0.3)
        cprint(f'Placing ask order for optimal ask_two: {size}', 'light_green', 'on_magenta')
        spot_order(exchange, coin, False, size, ask_two)
    
    if not resting_orders_ask[2] and math.floor(coin_inv) > 0:
        size = math.floor(coin_inv * 0.2)
        cprint(f'Placing ask order for optimal ask_three: {size}', 'light_green', 'on_magenta')
        spot_order(exchange, coin, False, size, ask_three)
    


    