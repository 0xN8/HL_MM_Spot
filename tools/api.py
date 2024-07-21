import time

minuteMs = 60000
candleSpread = 500


def postCandleSnapshot(hyperClass, coin, intervalStr, intervalInt):

    timeDiff = minuteMs * candleSpread * intervalInt
    endTime = int(time.time() * 1000)
    startTime = endTime - timeDiff

    response = hyperClass.info.candles_snapshot(coin, intervalStr, startTime, endTime)
    print("Candle's: ", response)
    return response.json()



def postL2Book(hyperClass, coin):

    response = hyperClass.info.l2_snapshot(coin)
    print("L2 Book: ", response)
    return response.json()
