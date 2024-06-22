from tools.config import url, coin, ws_url, test_url, ws_test_url
from tools.utils import setup, ws_manager_run, ws_run, elapsed_time
from hjb_eq import hjb
from hft import hft
from avg_vol import avg_vol



    

def main():
    account, address, info, exchange = setup('spot', url)
    hft(info, exchange, coin, address, account)

main()

