from termcolor import cprint


#Print out spot account balances info if any
def spotPositions(hyperClass):
    spotUserState = hyperClass.info.spot_user_state(hyperClass.makerAddress)

    print("spot balances: ", spotUserState['balances'])

    return spotUserState['balances']

#Search for order info by order_id
def spotOrderQuery(hyperClass, orderId):
    # Query the order status by order-id
    orderStatus = hyperClass.info.query_order_by_oid(hyperClass.makerAddress, orderId)
    print("Order status by oid:", orderStatus)


def spotOpenOrders(hyperClass):
    # Query the open orders
    openOrders = hyperClass.info.open_orders(hyperClass.makerAddress)
    print("Open orders:", openOrders)

    return openOrders


#Place a spot order, returns order id
def spotOrder(hyperClass, coin, side, amt, price):
    # Place an order
    orderResult = hyperClass.exchange.order(coin, side, amt, price, {"limit": {"tif": "Gtc"}}) #coin, is_buy, qty, price, orderType
    print(orderResult)

    if orderResult["status"] == "ok": 
        status = orderResult["response"]["data"]["statuses"][0]
        print(status)


#Cancel an Order
def spotCancel(hyperClass, coin, orderId):
    # Cancel an order
    cancelResult = hyperClass.exchange.cancel(coin, orderId)
    print(cancelResult)


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
        orders.append({"coin": coin, "is_buy": True, "sz": stableSz[i], "limit_px": bids[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})
    
    for i in range(len(coin_sz)):
        orders.append({"coin": coin, "is_buy": False, "sz": coinSz[i], "limit_px": asks[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})

    # Place multiple orders
    orderResult = hyperClass.exchange.bulk_orders(orders)

    if orderResult["status"] == "ok": 
        status = orderResult["response"]["data"]["statuses"]
        cprint(f"Order Status: {status}",'light_yellow', 'on_magenta')
    else:
        cprint("Order not submitted: {order_result}", 'white', 'on_red')
    
    