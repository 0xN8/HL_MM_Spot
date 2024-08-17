from tools.config import url, wsUrl, testUrl, wsTestUrl, coin
from models import tokens, defaults
from data.trades import tradeSub
from hft import hft_thread


    
#todo: import coin directly into tradeSub
def main():
    hyperClass = defaults.HyperMarketMakerDefaults(url, prod = True)
    tokensInfo = tokens.TokenInfo(hyperClass.info)
    token = tokensInfo.getToken()
    hft_thread(hyperClass, token)

    # tradeSub(hyperClass, coin)
main()

