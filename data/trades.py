
import numpy as np
import os



def average_time_between_trades(trades_data):
    # Calculate the differences between consecutive trades
    time_diffs = np.diff(trades_data)

    # Calculate and return the average time difference
    return np.mean(time_diffs)



def callback(data):

    if os.path.exists('trades.npy'):
        trades_data = np.load('trades.npy')
    else:
        trades_data = np.array([])

    data = data['data']
    for point in data:
        time = point['time']
        trades_data = np.append(trades_data, time)

    np.save('data/trades.npy', trades_data)

    print("Historical Trade Data: ", np.load('data/trades.npy'))
    avg_time = average_time_between_trades(trades_data)
    print("Average Time Between Trades: ", avg_time)


def trade_sub(info, coin):
    body = {
        "type": "trades",
        "coin": coin
    }

    info.subscribe(body, callback)


