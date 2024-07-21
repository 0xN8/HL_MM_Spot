

# bid_deque = collections.deque(maxlen=30)
# ask_deque = collections.deque(maxlen=30)
# mids_deque = collections.deque(maxlen=30)
# spreads_deque = collections.deque(maxlen=30)




# def callback_deque(data):
#     bid = float(data['data']['levels'][0][0]['px'])
#     ask = float(data['data']['levels'][1][0]['px'])
#     spread = ask - bid
#     mid = spread/2 + bid
    
#     if len(bid_deque) == bid_deque.maxlen:
#         bid_deque.popleft()

#     bid_deque.append(bid)

#     if len(ask_deque) == ask_deque.maxlen:
#         ask_deque.popleft()
    
#     ask_deque.append(ask)

#     if len(mids_deque) == mids_deque.maxlen:
#         mids_deque.popleft()
    
#     mids_deque.append(mid)

#     if len(spreads_deque) == spreads_deque.maxlen:
#         spreads_deque.popleft()
    
#     spreads_deque.append(spread)




# def hft_deque(info, exchange, coin, address):
#     body = {
#         "type": "l2Book",
#         "coin": coin
#     }

#     threading.Thread(target = info.subscribe, args = (body, callback_last)).start()

#     while True:
#         if len(bid_deque) > 3 and len(ask_deque) > 3:
#             cprint(f"Best Bids: {list(bid_deque)}", 'light_cyan')
#             cprint(f"Best Asks: {list(ask_deque)}", 'light_magenta')
#             last_bids = [x + 0.00001 for x in list(bid_deque)[-3:]]
#             last_asks = [x - 0.00001 for x in list(ask_deque)[-3:]]
#             bid_list = [round(num, 5) for num in last_bids]
#             ask_list = [round(num, 5) for num in last_asks]
#             skip = False

#             cprint(f"My Bids:{bid_list}", 'light_green', 'on_blue')
#             cprint(f"My Asks: {last_asks}", 'light_green', 'on_blue')
#             #if the last bid is greater than the last ask, we have a crossed market
#             #we should not trade in this case
#             for i in range(3):
#                 for j in range(3):
#                     if bid_list[i] > ask_list[j]:
#                         skip = True
#                         break
#                 if skip:
#                     break

#             if skip:
#                 print("Crossed Market, Skipping...")
#                 continue

#             last_mid = list(mids_deque)[-1]
#             last_spreads = list(spreads_deque)[-3:]

#             balances = spot_positions(address, info)
#             stables = None
#             coins = None
#             coin_short = coin.replace("/USDC", "")

#             for balance in balances:
#                 if balance['coin'] == 'USDC':
#                     stables = float(balance['total'])
#                 elif balance['coin'] == coin_short:
#                     coins = float(balance['total'])

#             stable_sz = [math.floor(sz) for sz in calc_sz(stables / last_mid, last_mid)]
#             coin_sz = [math.floor(sz) for sz in calc_sz(coins, last_mid)]
            

#             cprint(f"Stables: {stable_sz}", 'light_green', 'on_blue')
#             cprint(f"Coins: {stable_sz}", 'light_green', 'on_blue')

#             cprint(f"Last Mid: {round(last_mid, 5)}", 'light_green', 'on_blue')
#             cprint(f"Last Spreads: {[round(num, 5) for num in last_spreads]}", 'light_green', 'on_blue')

#             multi_spot_orders(exchange, coin, stable_sz,coin_sz, bid_list, ask_list)
#             time.sleep(2)
#             cancel_orders(exchange, info, address, coin)