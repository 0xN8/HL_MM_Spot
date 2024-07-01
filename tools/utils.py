from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from tools.env import get_env
import eth_account, time


def parse_parameters(parameters, prod):
    for parameter in parameters:
        if parameter['Name'] == '/HL-MM-Spot/dev/api' and not prod:
            api_key = parameter['Value']
        elif parameter['Name'] == '/HL-MM-Spot/prod/api' and prod:
            api_key = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/account-address':
            address = parameter['Value']
    return api_key, address


def setup(url, prod):
    parameters = get_env()
    api_key, address = parse_parameters(parameters, prod)
    account: LocalAccount = eth_account.Account.from_key(api_key)
    info = Info(url, skip_ws= False)
    exchange = Exchange(account, url, account_address=account.address)


    # Set address to the api address if no wallet is provided
    if address == "":
        address = account.address

    return account, address, info, exchange



def elapsed_time():
    while True:
        start_time = time.time() * 1000
        elapsed_time = time.time()*1000 - start_time

        print(f"Elapsed time: {elapsed_time} ms")