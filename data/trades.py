
import numpy as np
import os
from termcolor import cprint



def avgTimeTradeDelta(tradesData):
    # Calculate the differences between consecutive trades
    timeDiffs = np.diff(tradesData)

    # Calculate and return the average time difference
    return np.mean(timeDiffs)



def callback(data):

    if os.path.exists('trades.npy'):
        tradesData = np.load('trades.npy')
    else:
        tradesData = np.array([])

    data = data['data']
    for point in data:
        time = point['time']
        tradesData = np.append(tradesData, time)

    np.save('data/trades.npy', tradesData)

    cprint(f"Historical Trade Data: {np.load('data/trades.npy')}", 'light_cyan', 'on_dark_grey')
    avgTime = avgTimeTradeDelta(tradesData)
    cprint(f"Average Time Between Trades: {avgTime}", 'light_green', 'on_blue')


def tradeSub(hyperClass, coin):
    body = {
        "type": "trades",
        "coin": coin
    }

    hyperClass.info.subscribe(body, callback)


