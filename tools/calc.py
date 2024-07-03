import numpy as np


def round_to_sig_figs(num, sig_figs):
    if num != 0:
        return round(num, sig_figs - int(np.floor(np.log10(abs(num))) - 1))
    else:
        return 0
    
    
def calc_px(last_maker, buy):
    post_decimal = len(str(last_maker).split(".")[1]) if '.' in str(last_maker) else 0
    increment = 1/10**post_decimal
    if buy:
        return [last_maker, last_maker - increment, last_maker - 2*increment]
    else:
        return [last_maker, last_maker + increment, last_maker + 2*increment]
    

def calc_sz_list(inv, last_mid):
    min_sz = 10.05/last_mid
    des_sz = inv * 0.9
    if inv is None:
        return []
    
    sz = [inv * 0.4, inv * 0.3, inv * 0.2]
    
    #if the 40% is not a large enough, 30 and 20 will not be either
    #send the desired 90% in one order if possible
    if des_sz < min_sz:
        sz = []
    elif sz[0] < min_sz:
        sz = [inv * 0.9]
    
    #if 30% is not big enough we know 40% was, so send two orders one of 50% and one of 40%
    elif sz[1] < min_sz:
        sz = [inv * 0.5, inv * 0.4] 
    elif sz[2] < min_sz:
        sz = [inv * 0.3, inv * 0.3, inv * 0.3]

    return sz


def round_sz(sz, tick):
    subtractor = 10 ** -tick
    return [round(s, tick)-subtractor for s in sz]


# def volatility(close_prices):
#     close_prices_np = np.array(close_prices)

#     ratios = close_prices_np[1:] / close_prices_np[:-1]
#     log_returns = np.log(ratios)

#     return np.std(log_returns)
