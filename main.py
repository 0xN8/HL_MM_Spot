from hyperliquid.info import Info
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from dotenv import load_dotenv
import os
import eth_account
# import json





def main():

    load_dotenv()
    priv_key = os.getenv('Testnet_private_key')
    account: LocalAccount = eth_account.Account.from_key(priv_key)
    address = os.getenv('Testnet_address')

    if address == "":
        address = account.address
        print("Running with account address:", address)
    if address != account.address:
        print("Running with agent address:", account.address)


    # Get the user state and print out position information
    info = Info(constants.TESTNET_API_URL, skip_ws=True)
    user_state = info.user_state('needs to be main address')
    print("User Info: ", user_state)


    exchange = Exchange(account, constants.TESTNET_API_URL, account_address=address)
    

    positions = []
    for position in user_state["assetPositions"]:
        positions.append(position["position"])
    if len(positions) > 0:
        print("positions:")
        for position in positions:
            print(json.dumps(position, indent=2))
    else:
        print("no open positions")

    # Place an order that should rest by setting the price very low
    order_result = exchange.order("ETH", True, 0.05, 1100, {"limit": {"tif": "Gtc"}})
    print(order_result)

    # Query the order status by oid
    if order_result["status"] == "ok":
        status = order_result["response"]["data"]["statuses"][0]
        if "resting" in status:
            order_status = info.query_order_by_oid("0x2f6944608b311072f5ecb0f56e2b3d4cc74c5191", status["resting"]["oid"])
            print("Order status by oid:", order_status)

    # Cancel the order
    if order_result["status"] == "ok":
        status = order_result["response"]["data"]["statuses"][0]
        if "resting" in status:
            cancel_result = exchange.cancel("ETH", status["resting"]["oid"])
            print(cancel_result)


if __name__ == "__main__":
    main()