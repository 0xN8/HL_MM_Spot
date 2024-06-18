import json


#Print out spot account balances info if any
def spot_positions(address, info, exchange, coin):
    spot_user_state = info.spot_user_state(address)

    if len(spot_user_state["balances"]) > 0:
        print("spot balances:")
        for balance in spot_user_state["balances"]:
            print(json.dumps(balance, indent=2))
    else:
        print("no available token balances")

#Search for order info by order_id
def spot_order_query(order_id, info, address):
    # Query the order status by order-id
    order_status = info.query_order_by_oid(address, order_id)
    print("Order status by oid:", order_status)


#Place a spot order, returns order id
def spot_order(exchange, coin, side, amt, price):
    # Place an order
    order_result = exchange.order(coin, side, amt, price, {"limit": {"tif": "Gtc"}}) #coin, is_buy, qty, price, options
    print(order_result)

    if order_result["status"] == "ok": 
        status = order_result["response"]["data"]["statuses"][0]
        print(status)

#Cancel an Order
def spot_cancel(order_id, exchange, coin):
    # Cancel an order
    cancel_result = exchange.cancel(coin, order_id)
    print(cancel_result)


