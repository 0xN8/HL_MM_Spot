from tools.config import url, coin, ws_url, test_url, ws_test_url, coin_short
from tools.utils import setup, elapsed_time
from data.trades import trade_sub
from hjb_eq import hjb
from hft import hft
from avg_vol import avg_vol



    

def main():
    account, address, info, exchange = setup(url, prod=True)
    hft(info, exchange, coin, address, coin_short)
    # trade_sub(info, coin)
main()

