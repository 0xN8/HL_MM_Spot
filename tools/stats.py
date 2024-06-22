import numpy as np
from tools.api import post_candle_snapshot
import os

def volatility(close_prices):
    close_prices_np = np.array(close_prices)

    ratios = close_prices_np[1:] / close_prices_np[:-1]
    log_returns = np.log(ratios)

    return np.std(log_returns)



