from compute.stats import roundSigFigs
import collections, math
from termcolor import cprint
from tools.config import pxTick
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation



skewDeque = collections.deque([0], maxlen=200)


#calculates the futures funding I am paying to hedge
#appends basis as a percentage, if that percentage is positive
#that means I am getting paid to hedge. If I am getting paid
#I want to decrease my spread to get more fills
def basis(fundingsDeque, basisDeque):
    fRate = 0 # Decimal(fundingsDeque[-1]['fundingRate'])
    newBasis = Decimal(1/(1 + fRate * -1)-1)

    basisDeque.append(newBasis)
    cprint("Basis: " + str(newBasis), 'light_green', 'on_blue')



def skew(fills, orderBidDeque, orderAskDeque, wtAvgHalfSpreadPct):
    totalSzQuote = 0
    deltaPos = 0
    bidSz = 0
    askSz = 0
    
    for fill in fills:
            try:
                if fill['side'] == 'A':
                    deltaPos = -1 *(Decimal(fill['sz']) - Decimal(fill['fee']))
                elif fill['side'] == 'B':
                    deltaPos = Decimal(fill['sz']) - Decimal(fill['fee'])
            except InvalidOperation:
                cprint("Invalid Operation Fills", 'white', 'on_red')
                continue
        
    for orderBid in orderBidDeque:
        try:
            bidSz += Decimal(orderBid['sz'])
        except InvalidOperation:
            cprint("Invalid Operation Orders 1", 'white', 'on_red')
            continue
    for orderAsk in orderAskDeque:
        try:
            askSz += Decimal(orderAsk['sz'])
        except InvalidOperation:
            cprint("Invalid Operation Orders 2", 'white', 'on_red')
            continue
    
    totalSzQuote = max(bidSz, askSz)

    if totalSzQuote != 0:

        newSkew = (deltaPos/totalSzQuote) * wtAvgHalfSpreadPct * -1
        skewDeque.append(newSkew)
        cprint("Skew: " + str(newSkew), 'light_green', 'on_blue')
    else:
        cprint("Total Sz Quote is 0", 'white', 'on_red')


def calcMid (midDeque, newMidDeque):
    mid = midDeque[-1]
    skew = skewDeque[-1]
    makerFee = Decimal(.0001)
    newMid = roundSigFigs(mid * (1 + skew) * (1 - makerFee), 5)
    newMidDeque.append(newMid)
    cprint("Fair Price: " + str(newMid), 'light_green', 'on_blue')



def calcQuote(newBidDeque, newAskDeque, newMidDeque, avgHalfSpreadPct):
    newBid = roundSigFigs(newMidDeque[-1] * (1 - avgHalfSpreadPct), 5)
    newAsk = roundSigFigs(newMidDeque[-1] * (1 + avgHalfSpreadPct), 5)

    newBidDeque.append(newBid)
    newAskDeque.append(newAsk)
    cprint("Quoted New Bid: " + str(newBid), 'light_green', 'on_blue')
    cprint("Quoted New Ask: " + str(newAsk), 'light_green', 'on_blue')
    cprint(f"Quoted Spread: {newAsk - newBid}", 'light_green', 'on_blue')


def calcPrice(maker, buy):
    increment = Decimal(1)/Decimal(10**pxTick) #1 unit of the last decimal place
    print("Increment: ", increment)

    print("Maker1: ", maker)
    if buy:
        print("Maker2: ", maker - increment)
        print("Maker3: ", maker - 2*increment)
    else: 
        print("Maker2: ", maker + increment)
        print("Maker3: ", maker + 2*increment)

    if buy:
        return [maker, maker - increment, maker - 2*increment]
    else:
        return [maker, maker + increment, maker + 2*increment]
    

def calcSizeList(inv, fairMid):
    minOrderSize = Decimal(10.05)/fairMid
    maxSize = inv * Decimal(0.9)

    #if we don't hold any dollars/coins or the max size is too small for an order
    if inv is None or maxSize < minOrderSize:
        return []

    sz = [inv * Decimal(0.4), inv * Decimal(0.3), inv * Decimal(0.2)]
    
    #if the 40% is not a large enough, 30 and 20 will not be either
    #send the desired 90% in one order if possible
    if sz[0] < minOrderSize:
        sz = [inv * Decimal(0.9)]
    #if 30% is not big enough we know 40% was, so send two orders one of 50% and one of 40%
    elif sz[1] < minOrderSize:
        sz = [inv * Decimal(0.5), inv * Decimal(0.4)] 
    elif sz[2] < minOrderSize:
        sz = [inv * Decimal(0.3), inv * Decimal(0.3), inv * Decimal(0.3)]

    return sz



def roundSize(sz, szTick):
    # Create a new Decimal with the desired number of decimal places
    quantize_pattern = Decimal('0.' + '0' * szTick)
    return [s.quantize(quantize_pattern, rounding=ROUND_HALF_UP) for s in sz]

