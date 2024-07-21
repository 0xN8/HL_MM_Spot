
import numpy as np
import os



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

    print("Historical Trade Data: ", np.load('data/trades.npy'))
    avgTime = avgTimeTradeDelta(tradesData)
    print("Average Time Between Trades: ", avgTime)


def tradeSub(hyperClass, coin):
    body = {
        "type": "trades",
        "coin": coin
    }

    hyperClass.info.subscribe(body, callback)


