from trading.spot import multiSpotOrders, spotPositions, cancelOrders
from compute.stats import roundSigFigs
from compute.spread import calcQuote, calcSizeList, roundSize, skew, basis, calcMid, calcPrice
from models.deques import orderInit, fillInit
from tools.api import subFills, subOrders, subl2Book, subFundings
from termcolor import cprint
import threading, collections, time, json
from decimal import Decimal, ROUND_HALF_UP


#This is current/historic book data deque's
bidDeque = collections.deque(maxlen=200)
askDeque = collections.deque(maxlen=200)
midDeque = collections.deque(maxlen=200)
spreadDeque = collections.deque(maxlen=200)

#FillsDeques keep track of positions
#OrderDeques keep track of pending orders
fillsAskDeque = collections.deque(fillInit, maxlen=200)
fillsBidDeque = collections.deque(fillInit, maxlen=200)
orderAskDeque = collections.deque(orderInit,maxlen=200)
orderBidDeque = collections.deque(orderInit,maxlen=200)


fundingsDeque = collections.deque(maxlen=200)
basisDeque = collections.deque([0], maxlen=200)

#These are my deque's
newAskDeque = collections.deque(maxlen=1)
newBidDeque = collections.deque(maxlen=1)
newMidDeque = collections.deque(maxlen=1)
newSpreadDeque = collections.deque(maxlen=1)


#What's relevant is if the mid is the mid is different we need to recalc fair value and requote
#if the spread is different we need to requote around our old fair value
#hence if bid or ask is different we have either a new mid or a new spread
def l2BookSubCallback(ws, data):
    # cprint(f"L2Book Callback {data}", 'light_cyan', 'on_dark_grey')
    data = json.loads(data)
    if data['channel'] == 'subscriptionResponse':
        return
    
    bid = Decimal(data['data']['levels'][0][0]['px'])
    ask = Decimal(data['data']['levels'][1][0]['px'])
    spread = ask - bid
    mid = roundSigFigs(Decimal(spread/2) + bid, 5)
    makerDesProfit = 0


    if bidDeque and askDeque:
        if bid == bidDeque[-1] and ask == askDeque[-1]:
            print("No New Best Bid and Ask")
            return
    
    if not newMidDeque:
        newMidDeque.append(mid)

    bidDeque.append(bid)
    askDeque.append(ask)
    midDeque.append(mid)
    spreadDeque.append(spread)
    cprint(f'Market Mid & Spread: {mid}, {spread}', 'light_cyan', 'on_dark_grey')


    #this new spread takes the basis % and if basis is positive I am getting paid to hedge
    #(decrease spread --> more fills)
    #makerDesProfit is a % that I determine to increase or decrease spread width
    newSpreadDeque.append(spread*basisDeque[-1]*-1 + spread + makerDesProfit*spread)

    if len(midDeque) > 1 and midDeque[-1] != midDeque[-2]:
        calcMid(midDeque, newMidDeque)
        calcQuote(newBidDeque, newAskDeque, newMidDeque, avgHalfSpreadPct = (newSpreadDeque[-1]/2)/midDeque[-1])
        print("New Mid Calculated, calling HFT")
        hft()
    
    elif len(spreadDeque) > 1 and spreadDeque[-1] != spreadDeque[-2]:
        calcQuote(newBidDeque, newAskDeque, newMidDeque, avgHalfSpreadPct = (newSpreadDeque[-1]/2)/midDeque[-1])
        print("New Quote Calculated, calling HFT")
        hft()
        

#change in position size
def fillsSubCallback(ws, data):
    # cprint(f"Fills Callback {data}", 'light_cyan', 'on_dark_grey')
    data = json.loads(data)
    if data['channel'] == 'subscriptionResponse':
        return
    
    fills = data['data']['fills']
    if data['data'].get('isSnapshot') == None:
        for fill in fills:
            if fill['oid'] in orderAskDeque:
                orderAskDeque.remove(fills['oid'])
            elif fill['oid'] in orderBidDeque:
                orderBidDeque.remove(fills['oid'])
            if fill['side'] == 'A':
                fillsAskDeque.append(fill)
                cprint(f"New Asks Filled: {fill}", 'light_yellow', 'on_magenta')
            elif fill['side'] == 'B':
                fillsBidDeque.append(fill)
                cprint(f"New Bids Filled: {fill}", 'light_yellow', 'on_magenta')

        skew(fills, orderBidDeque, orderAskDeque, wtAvgHalfSpreadPct = (spreadDeque[-1]/2)/midDeque[-1])
        calcMid(midDeque, newMidDeque)
        calcQuote(newBidDeque, newAskDeque, newMidDeque, avgHalfSpreadPct = (newSpreadDeque[-1]/2)/midDeque[-1])
        hft()


#Just tracking orders for quote total
#But a change in order size will not trigger any new calculations
#Only fills, new mids, or new spreads will trigger new calculations
def ordersSubCallback(ws, data):
    # cprint(f"Orders Callback {data}", 'light_cyan', 'on_dark_grey')
    data = json.loads(data)
    if data['channel'] == 'subscriptionResponse':
        return

    orderData = data['data'][0]
    order = orderData['order']

    if orderData['status'] == 'open':
        if order['side'] == 'A':
            if order['oid'] not in orderAskDeque:
                orderAskDeque.append(order)
                cprint(f"Asks Order Added: {order}", 'light_yellow', 'on_magenta')
        if order['side'] == 'B':
            if order['oid'] not in orderBidDeque:
                orderBidDeque.append(order)
                cprint(f"Bids Order Added: {order}", 'light_yellow', 'on_magenta')

    elif orderData['status'] == 'canceled':
        if order['oid'] in orderAskDeque:
            orderAskDeque.remove(order['oid'])
        elif order['oid'] in orderBidDeque:
            orderBidDeque.remove(order['oid'])
    elif orderData['status'] == 'filled':
        if order['oid'] in orderAskDeque:
            orderAskDeque.remove(order['oid'])
        elif order['oid'] in orderBidDeque:
            orderBidDeque.remove(order['oid'])
    elif orderData['status'] == 'rejected':
        if order['oid'] in orderAskDeque:
            orderAskDeque.remove(order['oid'])
        elif order['oid'] in orderBidDeque:
            orderBidDeque.remove(order['oid'])



def fundingSubCallback(ws, data):
    # cprint(f"Funding Callback {data}", 'light_cyan', 'on_dark_grey')
    data = json.loads(data)
    if data['channel'] == 'subscriptionResponse' or data['channel'] == 'pong':
        cprint(f"Funding log: {data}", "magenta", "on_white")
        return

    fundings = data['data']['fundings']
    # if data['data']['isSnapshot']:
    #     for funding in fundings:
    #         fundingsDeque.append(funding)
    # else:
    fundingsDeque.append(fundings[-1])
    
    cprint(f"Fundings: {fundings[-1]}", 'light_yellow', 'on_magenta')
    basis(fundingsDeque, basisDeque)




def hft():
    cprint("HFT Taking Trade", 'light_cyan', 'on_dark_grey')
    global globalHyperClass, globalCoin, globalToken
    
    bids = calcPrice(newBidDeque.pop(), True)
    asks = calcPrice(newAskDeque.pop(), False)

    cprint(f"My Bids:{bids}", 'light_green', 'on_blue')
    cprint(f"My Asks: {asks}", 'light_green', 'on_blue')
    positions = spotPositions(globalHyperClass)

    coins = 0
    stables = 0
    szTick = globalToken['szDecimals']


    for position in positions:
        if position['coin'] == 'USDC':
            stables = Decimal(position['total'])
        elif position['coin'] == globalToken['name']:
            coins = Decimal(position['total'])

    cprint(f"Coins: {coins}", "light_cyan", "on_dark_grey")
    cprint(f"Stables: {stables}", "light_cyan", "on_dark_grey")
    #measured in dollars
    stableSz = roundSize(calcSizeList(stables / newMidDeque[-1], newMidDeque[-1]), szTick)
    coinSz = roundSize(calcSizeList(coins, newMidDeque[-1]), szTick)

    cprint(f"Stables Size List: {stableSz}", 'light_green', 'on_blue')
    cprint(f"Coins Size List: {coinSz}", 'light_green', 'on_blue')

    cancelOrders(globalHyperClass, globalCoin)
    multiSpotOrders(globalHyperClass, globalCoin, stableSz, coinSz, bids, asks)




def hft_thread(hyperClass, coin, token, wsUrl):
    global globalHyperClass, globalCoin, globalToken
    globalHyperClass = hyperClass
    globalCoin = coin
    globalToken = token
    l2BookThread = threading.Thread(target = subl2Book, args = ({"type": "l2Book","coin": coin}, l2BookSubCallback, wsUrl))
    fillsThread = threading.Thread(target = subFills, args = ({"type": "userFills","user": hyperClass.makerAddress}, fillsSubCallback, wsUrl))
    ordersThread = threading.Thread(target = subOrders, args = ({"type": "orderUpdates","user": hyperClass.makerAddress}, ordersSubCallback, wsUrl))
    fundingsThread = threading.Thread(target = subFundings, args = ({"type": "userFundings","user": hyperClass.hedgeAddress}, fundingSubCallback, wsUrl))
    # tradeThread = threading.Thread(target = hyperClass.info.subscribe, args = ({'type': 'trade', 'coin': coin}, tradeSubCallback, wsUrl))

    cprint("HFT Thread Started", 'light_cyan', 'on_dark_grey')

    l2BookThread.start()
    fillsThread.start()
    ordersThread.start()
    fundingsThread.start()
    # tradeThread.start()


    print("L2 Book Thread status: ", l2BookThread.is_alive())
    print("Fills Thread status: ", fillsThread.is_alive())
    print("Orders Thread status: ", ordersThread.is_alive())
    print("Fundings Thread status: ", fundingsThread.is_alive())


    

























#def oldHft(hyperClass, coin, token):

    # while True:
        # time.sleep(5) # default 50 ms (.05); 1 loop without delay ~ 400 ms
        #               #133 loops/min * 8 req/loop = 1064 weight/min < 1200 weight limit/min
        # if len(newBidDeque) > 0 and len(newAskDeque) > 0:
        #     myBid = newBidDeque[-1]
        #     myAsk = newAskDeque[-1]

        #     bids = calcPrice(bestBid, True)
        #     asks = calcPrice(bestAsk, False)
        #     bids = [roundSigFigs(num, 5) for num in bids]
        #     asks = [roundSigFigs(num,5) for num in asks]
        #     mid = roundSigFigs((midDeque)[0], 5)
        #     spread = roundSigFigs(spreadDeque[0], 5)
        #     skip = False

            # cprint(f"Best Bid: {bestBid}", 'light_cyan')
            # cprint(f"Best Ask: {bestAsk}", 'light_magenta')
            # cprint(f"My Bids:{bids}", 'light_green', 'on_blue')
            # cprint(f"My Asks: {asks}", 'light_green', 'on_blue')

            #if the last bid is greater than the last ask, we have a crossed the spread
            #we should not trade in this case
            # for i in range(3):
            #     for j in range(3):
            #         if bids[i] > asks[j]:
            #             skip = True
            #             break
            #     if skip:
            #         break

            # if skip:
            #     print("Crossed Market, Skipping...")
            #     continue


            # balances = spotPositions(hyperClass)
            # coins = 0
            # stables = 0
            # szTick = token['szDecimals']


            # for balance in balances:
            #     if balance['coin'] == 'USDC':
            #         stables = float(balance['total'])
            #     elif balance['coin'] == token['name']:
            #         coins = float(balance['total'])

            # stableSz = roundSize(calcSizeList(stables / mid, mid), szTick)
            # coinSz = roundSize(calcSizeList(coins, mid), szTick)
            

            # cprint(f"Stables: {stableSz}", 'light_green', 'on_blue')
            # cprint(f"Coins: {coinSz}", 'light_green', 'on_blue')

            # cprint(f"Last Mid: {mid}", 'light_green', 'on_blue')
            # cprint(f"Last Spread: {spread}", 'light_green', 'on_blue')

            # cancelOrders(hyperClass, coin)
            # multiSpotOrders(hyperClass, coin, stableSz, coinSz, bids, asks)


