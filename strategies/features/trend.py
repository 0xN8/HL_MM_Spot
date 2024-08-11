import threading, json, collections
from decimal import Decimal
from models.deques import candleInit
from tools.config import trendSetter, wsUrl
from tools.api import subscribe, heartbeatSub

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

    if Decimal(candleDeque[-1]['c']) < Decimal(candleDeque[-1]['c'])*Decimal(0.96): #4% drop
        cprint("Trend is down", 'white', 'on_red')
        trendFlag = False
    elif Decimal(candleDeque[-1]['c']) > Decimal(candleDeque[-1]['c']):
        trendFlag = True


def getTrendFlag():
    return trendFlag


def trend():
    trendThread = threading.Thread(target = subscribe, args = ({"type": "candle", "coin": trendSetter, "interval": "4h"}, candleSubCallback, wsUrl))
    trendThread.start()
    print("Trend Thread status: ", trendThread.is_alive())