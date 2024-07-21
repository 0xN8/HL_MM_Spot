from tools.config import url, coin, wsUrl, testUrl, wsTestUrl, coinShort
from models import tokens, defaults
from data.trades import tradeSub
from hft import hft_thread



    

def main():
    hyperClass = defaults.HyperMarketMakerDefaults(url)
    tokensInfo = tokens.TokenInfo(hyperClass.info)
    token = tokensInfo.getToken(coinShort)
    hft_thread(hyperClass, coin, token)

    # tradeSub(hyperClass, coin)
main()

