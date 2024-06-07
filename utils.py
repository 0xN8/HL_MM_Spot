from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from dotenv import load_dotenv
import os
import eth_account

def setup(market, url):
    load_dotenv()
    priv_key = os.getenv('api_priv_key')
    account: LocalAccount = eth_account.Account.from_key(priv_key)
    address = os.getenv('wallet_address')
    info = Info(url, skip_ws=True)
    exchange = Exchange(account, url, account_address=account.address)


    # Set address to the api address if no wallet is provided
    if address == "":
        address = account.address
        print("Running with account address:", address)
    if address != account.address:
        print("Running with agent address:", account.address)

    # Get the account info based on market type
    if market == 'spot':
        user_state = info.spot_user_state(address)
    elif market == 'futures':
        user_state = info.user_state(address)
    else:
        print("Please provide a valid market type")
        return
    print("User Info: ", user_state)

    return account, address, info, exchange

