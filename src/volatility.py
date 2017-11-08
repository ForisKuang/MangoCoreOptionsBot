from buy import shares
from spread import calc_spread
import numpy as np
tix = {}
lin_reg = {}

def ack_register(msg, order):
    global tix, lin_reg
    secs = msg["case_meta"]["securities"]
    for sec, val in secs.iteritems():
        if sec not in tix:
            tix[str(sec)] = [val["starting_price"]]
            lin_reg[str(sec)] = [0]
        
def calc_reg(msg, order):
    global tix, lin_reg
    mkt_price = msg["market_state"]["last_price"]
    tick = msg["market_state"]["ticker"]
    if tick in tix:
        tix[str(tick)].append(mkt_price)
    else:
        tix[str(tick)] = [mkt_price]
    x = range(len(tix[str(tick)]))
    m, b = np.polyfit(x, tix[tick], 1)
    lin_reg[str(tick)].append(m)
    if abs(m) > 0.005:
        buy_off_vol(m, str(tick), order)
    else:
        calc_spread(msg, order)

def buy_off_vol(m, tick, order):
    global lin_reg
    if float(lin_reg[tick][-2]) == 0.0:
        order.addTrade(tick, True, 50)
    elif float(m) < 0 and float(lin_reg[tick][-2]) > 0:
        max_trade = max(int(0.75*shares[tick]), 10)
        order.addTrade(tick, False, max_trade)
    elif float(m) > 0 and float(lin_reg[tick][-2]) < 0:
        max_trade = max(int(0.5*shares[tick]), 10)
        order.addTrade(tick, True, max_trade)
    elif float(m) < 0:
        order.addTrade(tick, True, 10)
    elif float(m) > 0:
        if shares[tick] > 10:
            order.addTrade(tick, False, 10)
