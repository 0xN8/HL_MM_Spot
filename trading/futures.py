import json

#Print out futures account positions info if any
def futuresPositions(hyperClass):
    userState = hyperClass.info.user_state(hyperClass.makerAddress)

    positions = []
    for position in userState["assetPositions"]:
        positions.append(position["position"])
    if len(positions) > 0:
        print("positions:")
        for position in positions:
            print(json.dumps(position, indent=2))
    else:
        print("no open positions")



#Search for order info by order_id        
def futuresOrderQuery(hyperClass, orderId):

    order_status = hyperClass.info.query_order_by_oid(hyperClass.makerAddress, orderId)
    print("Order status by oid:", order_status)


#Place a futures order, returns order id
def futuresOrder(hyperClass):

    orderResult = hyperClass.exchange.order("ETH", True, 0.01, 1100, {"limit": {"tif": "Gtc"}})
    print(orderResult)

    if orderResult["status"] == "ok":
        status = orderResult["response"]["data"]["statuses"][0]
        if "resting" in status:
            orderId = status["resting"]["oid"]
    
    return orderId


#Cancel an Order
def futuresCancel(hyperClass, order_id):
            cancelResult = hyperClass.exchange.cancel("ETH", order_id)
            print(cancelResult)

