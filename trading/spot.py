from termcolor import cprint
from decimal import Decimal
import re, time


#Print out spot account balances info if any
def spotPositions(hyperClass):
    spotUserState = hyperClass.info.spot_user_state(hyperClass.makerAddress)

    return spotUserState['balances']



def spotOpenOrders(hyperClass):
    # Query the open orders
    openOrders = hyperClass.info.open_orders(hyperClass.makerAddress)

    return openOrders




def modifyMultiOrders(hyperClass, coin, stableSz, coinSz, bid, ask):
    modifyReq = []
    bidNum = 0
    askNum = 0
    
    #sz lists are the constraints on bid and ask, bid and ask will always be a list of 3 values
    #sz will be variable between 0-3 values
    for order in spotOpenOrders(hyperClass):
        if order['coin'] == coin:
            if order['side'] == 'B':
                modifyReq.append({"oid": order["oid"], "order": {"coin": coin, "is_buy": True, "sz": stableSz[bidNum], "limit_px": bid[bidNum], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False}})
                bidNum += 1
            elif order['side'] == 'A':
                modifyReq.append({"oid": order["oid"], "order": {"coin": coin, "is_buy": False, "sz": coinSz[askNum], "limit_px": ask[askNum], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False}})
                askNum += 1
    

        modifyResult = hyperClass.exchange.bulk_modify_orders_new(modifyReq)
    if modifyResult["status"] == "ok": 
        status = modifyResult["response"]["data"]["statuses"]
        cprint(f"Modify Status:{status}", 'light_yellow', 'on_magenta')
    else:
        cprint(f"Order not submitted: {modifyResult}", 'white', 'on_red')
    
    orders = []
    #if we have more _sz than we have sides to modify, we need to place more orders on that side    
    if bidNum < len(stableSz):
        for i in range(bidNum, len(stableSz)):
            orders.append({"coin": coin, "is_buy": True, "sz": stableSz[i], "limit_px": bid[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})

    if askNum < len(coinSz):
        for i in range(askNum, len(coinSz)):
            orders.append({"coin": coin, "is_buy": False, "sz": coinSz[i], "limit_px": ask[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})

    orderResult = hyperClass.exchange.bulk_orders(orders)

    if orderResult["status"] == "ok": 
        status = orderResult["response"]["data"]["statuses"]
        cprint(f"Excess Order Status: {status}",'light_yellow', 'on_magenta')
    else:
        cprint("Excess Order not submitted: {order_result}", 'white', 'on_red')




def cancelOrders(hyperClass, coin):
    cancelOrders = []
    for order in spotOpenOrders(hyperClass):
        if order['coin'] == coin:
            cancelOrders.append({'coin':coin, 'oid': order["oid"]})

    cancelResult = hyperClass.exchange.bulk_cancel(cancelOrders)

    if cancelResult["status"] == "ok": 
        status = cancelResult["response"]["data"]["statuses"]
        cprint(f"Cancel Order Status: {status}",'light_yellow', 'on_magenta')
    else:
        cprint("Cancel Order not submitted: {cancel_result}", 'white', 'on_red')



def multiSpotOrders(hyperClass, coin, stableSz, coinSz, bids, asks):
    orders = []
    
    for i in range(len(stableSz)):
        orders.append({"coin": coin, "is_buy": True, "sz": float(stableSz[i]), "limit_px": float(bids[i]), "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})
    
    for i in range(len(coinSz)):
        orders.append({"coin": coin, "is_buy": False, "sz": float(coinSz[i]), "limit_px": float(asks[i]), "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})

    cprint(f"Placing Orders: {orders}", 'light_yellow', 'on_magenta')
    # Place multiple orders
    orderResult = hyperClass.exchange.bulk_orders(orders)
    if orderResult["status"] == "ok":
        statuses = orderResult["response"]["data"]["statuses"]
        # for status in statuses:
        #     if "error" in status:
        #         errorMsg = status["error"]
        #         if errorMsg.startswith("Post only order would have immediately matched"):
        #             match = re.search(r'was\s(.*)\.', errorMsg)
        #             if match:
        #                 bbo = Decimal(match.group(1))
        #                 cprint(f"Post only order would have matched at {bbo}, resubmitting order", 'light_cyan', 'on_dark_grey')

        # get order id and find what side that order got rejected was on
        # can use index error was to find which order it is
                        

        # if we get a post only order would have immediately matched we can cancel all orders and let the subscriptions retry

        cprint(f"Order Status: {statuses}",'light_yellow', 'on_magenta')
    elif orderResult["status"] == 'err':
        errorMsg = orderResult["response"]
        if errorMsg.startswith("Too many cumulative requests sent"):
            cprint("Too many requests, submitting Taker order", 'white', 'on_red')
            time.sleep(10)
            if stableSz > coinSz:
                marketOrderResult = hyperClass.exchange.market_open(coin, True, float(sum(stableSz)))
                cprint(f"Market Order Status: {marketOrderResult}", 'light_yellow', 'on_magenta')
            else:
                marketOrderResult = hyperClass.exchange.market_open(coin, False, float(sum(coinSz)))
                cprint(f"Market Order Status: {marketOrderResult}", 'light_yellow', 'on_magenta')

    else:
        cprint(f"Order not submitted: {orderResult}", 'white', 'on_red')
    
    