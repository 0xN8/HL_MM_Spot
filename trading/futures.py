import json

#Print out futures account positions info if any
def futures_positions(address, info):
    user_state = info.user_state(address)

    positions = []
    for position in user_state["assetPositions"]:
        positions.append(position["position"])
    if len(positions) > 0:
        print("positions:")
        for position in positions:
            print(json.dumps(position, indent=2))
    else:
        print("no open positions")



#Search for order info by order_id        
def futures_order_query(order_id, info, address):

    order_status = info.query_order_by_oid(address, order_id)
    print("Order status by oid:", order_status)


#Place a futures order, returns order id
def futures_order(exchange):

    order_result = exchange.order("ETH", True, 0.01, 1100, {"limit": {"tif": "Gtc"}})
    print(order_result)

    if order_result["status"] == "ok":
        status = order_result["response"]["data"]["statuses"][0]
        if "resting" in status:
            order_id = status["resting"]["oid"]
    
    return order_id


#Cancel an Order
def futures_cancel(order_id, exchange):
            cancel_result = exchange.cancel("ETH", order_id)
            print(cancel_result)

