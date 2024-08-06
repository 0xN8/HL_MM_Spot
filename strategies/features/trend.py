import threading, json, collections
from models.deques import candleInit
from decimal import Decimal

candleDeque = collections.deque(candleInit, maxlen=200)
trendFlag = True

def candleSubCallback(ws, data):
    global trendFlag
    data = json.loads(data)

    if data['channel'] == 'subscriptionResponse':
        return
    
    candle = data["data"]

    if candle["T"] == candleDeque[-1]["T"]:
        candleDeque[-1] = candle
    else:
        candleDeque.append(candle)

    if candleDeque[-1]['c'] < candleDeque[-1]['c']*Decimal(0.96): #4% drop
        trendFlag = False
    elif candleDeque[-1]['c'] > candleDeque[-1]['c']:
        trendFlag = True


def getTrendFlag():
    return trendFlag


def trend(subCandles, hedge, wsUrl):
    trendThread = threading.Thread(target = subCandles, args = ({"type": "candle", "coin": hedge, "interval": "4h"}, candleSubCallback, wsUrl))