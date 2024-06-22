from tools.api import post_l2_book
import numpy as np



def load_spread_history(coin):
    data_path = 'data/spreads.npy'
    l2_res = post_l2_book(coin)
    bid = l2_res['levels'][0][0]['px']
    ask = l2_res['levels'][1][0]['px']
    print("Bid: ", bid)
    print("Ask: ", ask)
    spread = float(ask) - float(bid)

    # Load the existing spreads from the file, if it exists
    if os.path.exists(data_path):
        spread_data = np.load(data_path)
    else:
        spread_data = np.array([])

    # If the array has more than 30 items, remove the first one
    if len(spread_data) >= 30:
        spread_data = spread_data[1:]

    # Add the new spread to the array
    spread_data = np.append(spread_data, spread)#FIFO


    # Write the updated array back to the file
    np.save (data_path, spread_data)

    print("Historical Spread Data: ", np.load(data_path))

def avg_vol(coin):
    load_spread_history(coin)