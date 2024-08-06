
import websocket, threading, json, time
from termcolor import cprint


def on_open(ws, msg):
    cprint(f"### opened ### {msg}", "magenta", "on_white")
    ws.send(json.dumps(msg))

def on_error(ws, error):
    cprint({error}, "white", "on_red")

def on_close(ws, *args):
    cprint(f"### closed ### {args}", "white", "on_red")
    cprint("WebSocket connection closed, attempting to reconnect...", "magenta", "on_white")
    time.sleep(3)  # wait for 3 seconds before attempting to reconnect
    reconnect(ws)



def reconnect(ws):
    while True:
        try:
            ws.run_forever()
        except Exception as e:
            cprint("Error while reconnecting, trying again in 3 seconds...", "white", "on_red")
            time.sleep(3)


def send_ping(ws):
    while True:
        time.sleep(55)
        ws.send(json.dumps({ "method": "ping" }))




def subFills(args, callback, url):

    msg = {
        "method": "subscribe",
        "subscription": args
    }

    ws = websocket.WebSocketApp(url, on_message = callback, on_error = on_error, on_close = on_close)
    ws.on_open = lambda ws: on_open(ws, msg)
    ws.run_forever()



def subOrders(args, callback, url):

    msg = {
        "method": "subscribe",
        "subscription": args
    }

    ws = websocket.WebSocketApp(url, on_message = callback, on_error = on_error, on_close = on_close)
    ws.on_open = lambda ws: on_open(ws, msg)
    ws.run_forever()




def subl2Book(args, callback, url):
    msg = {
        "method": "subscribe",
        "subscription": args
    }

    ws = websocket.WebSocketApp(url, on_message = callback, on_error = on_error, on_close = on_close)
    ws.on_open = lambda ws: on_open(ws, msg)
    ws.run_forever() 

    
def subFundings (args, callback, url):
    msg = {
        "method": "subscribe",
        "subscription": args
    }

    ws = websocket.WebSocketApp(url, on_message = callback, on_error = on_error, on_close = on_close)
    ws.on_open = lambda ws: ws.send(json.dumps(msg))
    heartbeat = threading.Thread(target = send_ping, args = (ws,),)
    heartbeat.start()
    ws.run_forever()





minuteMs = 60000
candleSpread = 500




def postCandleSnapshot(hyperClass, coin, intervalStr, intervalInt):

    timeDiff = minuteMs * candleSpread * intervalInt
    endTime = int(time.time() * 1000)
    startTime = endTime - timeDiff

    response = hyperClass.info.candles_snapshot(coin, intervalStr, startTime, endTime)
    return response.json()