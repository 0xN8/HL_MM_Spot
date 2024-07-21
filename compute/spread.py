import collections, math
from compute.calc import roundSigFigs



skewDeque = collections.deque(maxlen=200)


#calculates the futures funding I am paying to hedge
#appends basis as a percentage, if that percentage is positive
#that means I am getting paid to hedge. If I am getting paid
#I want to decrease my spread to get more fills
def basis(fundingsDeque, basisDeque):
    fRate = float(fundingsDeque[-1].fundingRate)
    basisDeque.append(1/(1 + fRate * -1)-1)



def skew(fills, orderBidDeque, orderAskDeque, wtAvgHalfSpreadPct):
    totalSzQuote = 0
    deltaPos = 0
    bidSz = 0
    askSz = 0
    
    for fill in fills:
            if fill.side == 'A':
                deltaPos = -1 *(fill.sz - fill.fee)
            elif fill.side == 'B':
                deltaPos = (fills.sz - fills.fee)
        
    for orderBid in orderBidDeque:
        bidSz += orderBid.sz
    for orderAsk in orderAskDeque:
        askSz += orderAsk.sz
    
    totalSzQuote = min(bidSz, askSz)

    skewDeque.append((deltaPos/totalSzQuote) * wtAvgHalfSpreadPct * -1)


def calcMid (midDeque, newMidDeque):
    mid = midDeque[-1]
    skew = skewDeque[-1]
    makerFee = .0001
    newMid = roundSigFigs(mid * (1 + skew) * (1 - makerFee),5)

    newMidDeque.append(newMid)


def calcQuote(newBidDeque, newAskDeque, newMidDeque, avgHalfSpreadPct):
    newBidDeque.append(roundSigFigs(newMidDeque[-1] * (1 - avgHalfSpreadPct), 5))
    newAskDeque.append(roundSigFigs(newMidDeque[-1] * (1 + avgHalfSpreadPct), 5))


def calcPrice(maker, buy):
    postDecimal = len(str(maker).split(".")[1]) if '.' in str(maker) else 0 #number of places to the right of the decimal
    increment = 1/10**postDecimal #1 unit of the last decimal place
    if buy:
        return [maker, maker - increment, maker - 2*increment]
    else:
        return [maker, maker + increment, maker + 2*increment]
    

def calcSizeList(inv, fairMid):
    minOrderSize = 10.05/fairMid
    maxSize = inv * 0.9

    #if we don't hold any dollars/coins or the max size is too small for an order
    if inv is None or maxSize < minOrderSize:
        return []

    sz = [inv * 0.4, inv * 0.3, inv * 0.2]
    
    #if the 40% is not a large enough, 30 and 20 will not be either
    #send the desired 90% in one order if possible
    if sz[0] < minOrderSize:
        sz = [inv * 0.9]
    #if 30% is not big enough we know 40% was, so send two orders one of 50% and one of 40%
    elif sz[1] < minOrderSize:
        sz = [inv * 0.5, inv * 0.4] 
    elif sz[2] < minOrderSize:
        sz = [inv * 0.3, inv * 0.3, inv * 0.3]

    return sz


def roundSize(sz, tick):
    subtractor = 10 ** -tick
    return [math.floor(s, tick) for s in sz]



