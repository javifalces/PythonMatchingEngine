# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 17:46:49 2019

@author: fmerlos
"""

import os
os.chdir('C:/DEV/PythonMatchingEngine')
import sys
sys.path.append('C:/DEV/PythonMatchingEngine')
import time
import pdb
import numpy as np
from orderbook.gateway import Gateway
from examples.algorithms import BuyTheBid, SimplePOV
from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd



# =============================================================================
# RESTART orderbook
# =============================================================================

gtw = Gateway(ticker='san',
             year=2019,
             month=5,
             day=23,
             start_h=9,
             end_h=10,
             latency=20000)
    


# =============================================================================
# RUN SIMPLEPOV ALGO
# =============================================================================


pov_algo = SimplePOV(is_buy=True, target_pov=0.2, lmtpx=np.Inf,
                       qty=int(1e6), sweep_max=3)


hist_bidask = list()
t = time.time()
ob_nord = gtw.ob_nord-1
while (not pov_algo.done) and (gtw.ob_time < gtw.stop_time):        
    hist_bidask.append([gtw.ob.bbidpx, gtw.ob.baskpx, gtw.ob_time])
    pov_algo.eval_and_act(gtw)        
    gtw.tick()    
print(time.time()-t)





# =============================================================================
# PLOTTING THE ALGO RESULT 
# =============================================================================


## orderbook BIDASK
bidask = pd.DataFrame(hist_bidask, columns=['bid', 'ask', 'timestamp'])
bidask.set_index(bidask.timestamp, inplace=True)
# orderbook TRADES 
trades = pd.DataFrame(gtw.ob.trades).loc[:gtw.ob.ntrds-1]
trades.set_index(trades.timestamp, inplace=True)
# MY TRADES 
my_trades = pd.DataFrame(gtw.ob.my_trades).loc[:gtw.ob.my_ntrds-1]
my_trades.set_index(my_trades.timestamp, inplace=True)

# filter:

plt.figure(num=1, figsize=(20, 10))
start_t = bidask.index[0]
win_size = 120
win_move = 20

for i in range(200):
    end_t = start_t + timedelta(0,win_size)    
    subbidask = bidask.loc[start_t:end_t]
    subtrades = trades.loc[start_t:end_t]
    mysubtrades = my_trades.loc[start_t:end_t]
    
    greenc = '#009900'
    redc = '#cc0000'

    plt.plot(subbidask.bid, color=greenc, label='bid1')
    plt.plot(subbidask.ask, color=redc, label='ask1')
    
    idx_buy_init = np.where(subtrades.buy_init * (subtrades.agg_ord > 0))
    idx_sell_init = np.where(np.logical_not(subtrades.buy_init) * \
                             (subtrades.agg_ord > 0))
    buy_init_trd = subtrades.iloc[idx_buy_init]['price']
    sell_init_trd = subtrades.iloc[idx_sell_init]['price']
    
    idx_my_buy_init = np.where(mysubtrades.buy_init)
    idx_my_sell_init = np.where(np.logical_not(mysubtrades.buy_init))
    my_buy_init_trd = mysubtrades.iloc[idx_my_buy_init]['price']
    my_sell_init_trd = mysubtrades.iloc[idx_my_sell_init]['price']
    
    plt.plot(buy_init_trd, color=greenc, linestyle=' ', marker='^', 
             markersize=12, label='aggbuy')
    plt.plot(sell_init_trd, color=redc, linestyle=' ', marker='v', 
             markersize=12, label='aggsell')
    
    plt.plot(my_buy_init_trd, color='blue', linestyle=' ', marker='^', 
             markersize=7, label='aggbuy')
    plt.plot(my_sell_init_trd, color=redc, linestyle=' ', marker='v', 
             markersize=7, label='aggsell')
    
    plt.legend()
    plt.show(block=False)
    
    input("Click to advance")
    
    start_t += timedelta(0, win_move) 
    plt.clf()