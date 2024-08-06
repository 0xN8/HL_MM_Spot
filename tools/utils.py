from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from eth_account.signers.local import LocalAccount
from tools.env import getEnv
import eth_account, time


def parseParameters(parameters, prod):
    for parameter in parameters:
        if parameter['Name'] == '/HL-MM-Spot/dev/api' and not prod:
            apiKey = parameter['Value']
        elif parameter['Name'] == '/HL-MM-Spot/prod/api' and prod:
            apiKey = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/account-address':
            accAddress = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/mm_address':
            makerAddress = parameter['Value']
        elif parameter['Name'] == '/HyperLiquid/prod/neu-address':
            hedgeAddress = parameter['Value']
    return apiKey, accAddress, makerAddress, hedgeAddress


def setup(url, prod):
    parameters = getEnv()
    apiKey, accAddress, makerAddress, hedgeAddress = parseParameters(parameters, prod)
    account: LocalAccount = eth_account.Account.from_key(apiKey)
    info = Info(url, skip_ws= False)
    exchange = Exchange(account, url, vault_address=makerAddress)


    # Set address to the api address if no wallet is provided
    if accAddress == "":
        address = account.address

    return account, accAddress, makerAddress, hedgeAddress, info, exchange



def elapsedTime():
    while True:
        startTime = time.time() * 1000
        elapsedTime = time.time()*1000 - startTime

        cprint(f"Elapsed time: {elapsedTime} ms", 'light_cyan', 'on_dark_grey')