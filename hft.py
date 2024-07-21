from trading.spot import multiSpotOrders, spotPositions, cancelOrders
from compute.calc import roundSigFigs
from compute.spread import calcQuote, calcSizeList, roundSize, skew, basis, calcMid, calcPrice
from termcolor import cprint
import threading, collections, time


#This is current/historic book data deque's
bidDeque = collections.deque(maxlen=200)
askDeque = collections.deque(maxlen=200)
midDeque = collections.deque(maxlen=200)
spreadDeque = collections.deque(maxlen=200)

#FillsDeques keep track of positions
#OrderDeques keep track of pending orders
fillsAskDeque = collections.deque(maxlen=200)
fillsBidDeque = collections.deque(maxlen=200)
orderAskDeque = collections.deque(maxlen=200)
orderBidDeque = collections.deque(maxlen=200)
fundingsDeque = collections.deque(maxlen=200)
basisDeque = collections.deque(maxlen=200)

#These are my deque's
newAskDeque = collections.deque(maxlen=1)
newBidDeque = collections.deque(maxlen=1)
newMidDeque = collections.deque(maxlen=1)
newSpreadDeque = collections.deque(maxlen=1)


#What's relevant is if the mid is the mid is different we need to recalc fair value and requote
#if the spread is different we need to requote around our old fair value
#hence if bid or ask is different we have either a new mid or a new spread
def l2BookSubCallback(data):
    bid = float(data['data']['levels'][0][0]['px'])
    ask = float(data['data']['levels'][1][0]['px'])
    spread = ask - bid
    mid = spread/2 + bid
    makerDesProfit = 0



    if bid == bidDeque[-1] and ask == askDeque[-1]:
        return
    
    bidDeque.append(bid)
    askDeque.append(ask)
    midDeque.append(roundSigFigs(mid,5))
    spreadDeque.append(spread)
    #this new spread takes the basis % and if basis is positive I am getting paid to hedge
    #(decrease spread --> more fills)
    #makerDesProfit is a % that I determine to increase or decrease spread width
    newSpreadDeque.append(spread*basisDeque[-1]*-1 + spread + makerDesProfit*spread)

    if midDeque[-1] != midDeque[-2]:
        calcMid(midDeque, newMidDeque)
        calcQuote(newMidDeque, avgHalfSpreadPct = (newSpreadDeque[-1]/2)/midDeque[-1])
        hft()

    elif spreadDeque[-1] != spreadDeque[-2]:
        calcQuote(newMidDeque, avgHalfSpreadPct = (newSpreadDeque[-1]/2)/midDeque[-1])
        hft()
        

#change in position size
def fillsSubCallback(data):
    fills = data.data.fills
    if not data.data.isSnapshot:
        for fill in fills:
            if fill.oid in orderAskDeque:
                orderAskDeque.remove(fills.oid)
            elif fill.oid in orderBidDeque:
                orderBidDeque.remove(fills.oid)
            if fill.side == 'A':
                fillsAskDeque.append(fill)
                cprint(f"AsksFilled: {fillsAskDeque}")
            elif fill.side == 'B':
                fillsBidDeque.append(fill)
                cprint(f"BidsFilled: {fillsBidDeque}")

        skew(fills, orderBidDeque, orderAskDeque, wtAvgHalfSpreadPct = (spreadDeque[-1]/2)/midDeque[-1])
        calcMid(midDeque, newMidDeque)
        calcQuote(newMidDeque, avgHalfSpreadPct = (newSpreadDeque[-1]/2)/midDeque[-1])
        hft()


#Just tracking orders for quote total
#But a change in order size will not trigger any new calculations
#Only fills, new mids, or new spreads will trigger new calculations
def ordersSubCallback(data):
    orderData = data.data[0]
    order = orderData.order

    if orderData.status == 'open':
        if order.side == 'A':
            if order.oid not in orderAskDeque:
                orderAskDeque.append(order)
                cprint(f"Asks Orders: {orderAskDeque}")
        if order.side == 'B':
            if order.oid not in orderBidDeque:
                orderBidDeque.append(order)
                cprint(f"Bids Orders: {orderBidDeque}")

    elif orderData.status == 'canceled':
        if order.oid in orderAskDeque:
            orderAskDeque.remove(order.oid)
        elif order.oid in orderBidDeque:
            orderBidDeque.remove(order.oid)
    elif orderData.status == 'filled':
        if order.oid in orderAskDeque:
            orderAskDeque.remove(order.oid)
        elif order.oid in orderBidDeque:
            orderBidDeque.remove(order.oid)
    elif orderData.status == 'rejected':
        if order.oid in orderAskDeque:
            orderAskDeque.remove(order.oid)
        elif order.oid in orderBidDeque:
            orderBidDeque.remove(order.oid)



def fundingSubCallback(data):
    fundings = data.data.fundings
    if data.data.isSnapshot:
        for funding in fundings:
            fundingsDeque.append(funding)
    else:
        fundingsDeque.append(fundings[-1])
    
    basis(fundingsDeque, basisDeque)




def hft():
    global globalHyperClass, globalCoin, globalToken

    bids = calcPrice(newBidDeque.pop(), True)
    asks = calcPrice(newAskDeque.pop(), False)

    positions = spotPositions(globalHyperClass)

    coins = 0
    stables = 0
    szTick = globalToken['szDecimals']


    for position in positions:
        if position['coin'] == 'USDC':
            stables = float(position['total'])
        elif position['coin'] == globalToken['name']:
            coins = float(position['total'])

    #measured in dollars
    stableSz = roundSize(calcSizeList(stables / newMidDeque[-1], newMidDeque[-1]), szTick)
    coinSz = roundSize(calcSizeList(coins, newMidDeque[-1]), szTick)
    

    # cprint(f"Stables: {stableSz}", 'light_green', 'on_blue')
    # cprint(f"Coins: {coinSz}", 'light_green', 'on_blue')

    # cprint(f"Last Mid: {mid}", 'light_green', 'on_blue')
    # cprint(f"Last Spread: {spread}", 'light_green', 'on_blue')

    cancelOrders(globalHyperClass, globalCoin)
    multiSpotOrders(globalHyperClass, globalCoin, stableSz, coinSz, bids, asks)




def hft_thread(hyperClass, coin, token):
    global globalHyperClass, globalCoin, globalToken
    globalHyperClass = hyperClass
    globalCoin = coin
    globalToken = token
    threading.Thread(target = hyperClass.info.subscribe, args = ({"type": "l2Book","coin": coin}, l2BookSubCallback)).start()
    threading.Thread(target = hyperClass.info.subscribe, args = ({"type": "userFills","user": hyperClass.makerAddress}, fillsSubCallback)).start()
    threading.Thread(target = hyperClass.info.subscribe, args = ({"type": "orderUpdates","user": hyperClass.makerAddress}, ordersSubCallback)).start()
    threading.Thread(target = hyperClass.info.subscribe, args = ({"type": "userFundings","user": hyperClass.hedgeAddress}, fundingSubCallback)).start()
    cprint("HFT Thread Started", 'light_green', 'on_blue')
    # threading.Thread(target = hyperClass.info.subscribe, args = ({'type': 'trade', 'coin': coin}, tradeSubCallback)).start()

























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


