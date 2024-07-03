from termcolor import colored, cprint
import math


#Print out spot account balances info if any
def spot_positions(address, info):
    spot_user_state = info.spot_user_state(address)

    print("spot balances: ", spot_user_state['balances'])

    return spot_user_state['balances']

#Search for order info by order_id
def spot_order_query(order_id, info, address):
    # Query the order status by order-id
    order_status = info.query_order_by_oid(address, order_id)
    print("Order status by oid:", order_status)


def spot_open_orders(info, address):
    # Query the open orders
    open_orders = info.open_orders(address)
    print("Open orders:", open_orders)

    return open_orders


#Place a spot order, returns order id
def spot_order(exchange, coin, side, amt, price):
    # Place an order
    order_result = exchange.order(coin, side, amt, price, {"limit": {"tif": "Gtc"}}) #coin, is_buy, qty, price, orderType
    print(order_result)

    if order_result["status"] == "ok": 
        status = order_result["response"]["data"]["statuses"][0]
        print(status)


#Cancel an Order
def spot_cancel(order_id, exchange, coin):
    # Cancel an order
    cancel_result = exchange.cancel(coin, order_id)
    print(cancel_result)


def modify_multi_orders(exchange, info, address,  coin, stable_sz, coin_sz, bid, ask):
    modify_req = []
    bid_i = 0
    ask_i = 0
    
    #sz lists are the constraints on bid and ask, bid and ask will always be a list of 3 values
    #sz will be variable between 0-3 values
    for order in spot_open_orders(info, address):
        if order['coin'] == coin:
            if order['side'] == 'B':
                modify_req.append({"oid": order["oid"], "order": {"coin": coin, "is_buy": True, "sz": stable_sz[bid_i], "limit_px": bid[bid_i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False}})
                bid_i += 1
            elif order['side'] == 'A':
                modify_req.append({"oid": order["oid"], "order": {"coin": coin, "is_buy": False, "sz": coin_sz[ask_i], "limit_px": ask[ask_i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False}})
                ask_i += 1
    

        modify_result = exchange.bulk_modify_orders_new(modify_req)
    if modify_result["status"] == "ok": 
        status = modify_result["response"]["data"]["statuses"]
        cprint(f"Modify Status:{status}", 'light_yellow', 'on_magenta')
    else:
        cprint(f"Order not submitted: {modify_result}", 'white', 'on_red')
    
    orders = []
    #if we have more _sz than we have sides to modify, we need to place more orders on that side    
    if bid_i < len(stable_sz):
        for i in range(bid_i, len(stable_sz)):
            orders.append({"coin": coin, "is_buy": True, "sz": stable_sz[i], "limit_px": bid[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})

    if ask_i < len(coin_sz):
        for i in range(ask_i, len(coin_sz)):
            orders.append({"coin": coin, "is_buy": False, "sz": coin_sz[i], "limit_px": ask[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})

    order_result = exchange.bulk_orders(orders)

    if order_result["status"] == "ok": 
        status = order_result["response"]["data"]["statuses"]
        cprint(f"Excess Order Status: {status}",'light_yellow', 'on_magenta')
    else:
        cprint("Excess Order not submitted: {order_result}", 'white', 'on_red')




def cancel_orders(exchange,info, address, coin):
    cancel_orders = []
    for order in spot_open_orders(info, address):
        if order['coin'] == coin:
            cancel_orders.append({'coin':coin, 'oid': order["oid"]})

    cancel_result = exchange.bulk_cancel(cancel_orders)

    if cancel_result["status"] == "ok": 
        status = cancel_result["response"]["data"]["statuses"]
        cprint(f"Cancel Order Status: {status}",'light_yellow', 'on_magenta')
    else:
        cprint("Cancel Order not submitted: {cancel_result}", 'white', 'on_red')



def multi_spot_orders(exchange, coin, stable_sz, coin_sz, bids, asks):
    orders = []
    
    for i in range(len(stable_sz)):
        orders.append({"coin": coin, "is_buy": True, "sz": stable_sz[i], "limit_px": bids[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})
    
    for i in range(len(coin_sz)):
        orders.append({"coin": coin, "is_buy": False, "sz": coin_sz[i], "limit_px": asks[i], "order_type": {"limit": {"tif": "Alo"}}, "reduce_only": False})

    # Place multiple orders
    order_result = exchange.bulk_orders(orders)

    if order_result["status"] == "ok": 
        status = order_result["response"]["data"]["statuses"]
        cprint(f"Order Status: {status}",'light_yellow', 'on_magenta')
    else:
        cprint("Order not submitted: {order_result}", 'white', 'on_red')
    
    