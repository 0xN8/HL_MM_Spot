from tools.config import url, coin, ws_url, test_url, ws_test_url, coin_short
from tools.utils import setup, elapsed_time
from models.tokens import TokenInfo
from data.trades import trade_sub
from hft import hft



    

def main():
    account, address, info, exchange = setup(url, prod=True)
    token_info = TokenInfo(info)
    token = token_info.get_token(coin_short)
    hft(info, exchange, address, coin, token)
    # trade_sub(info, coin)
main()

