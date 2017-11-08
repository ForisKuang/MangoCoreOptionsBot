import tradersbot as tt
import random

t = tt.TradersBot(host='127.0.0.1', id='trader0', password='trader0')
tick = 0
tickers = ['USDCHF', 'USDJPY', 'EURUSD', 'USDCAD', 'CHFJPY', 'EURJPY', 'EURCHF', 'EURCAD']

# Indicies chosen such that if '[x][y]' is a legitimate ticker,
# then index(x) < index(y).
country_to_index = {'EUR': 0, 'USD': 1, 'CHF': 2, 'JPY': 3, 'CAD': 4}
index_to_country = ['EUR', 'USD', 'CHF', 'JPY', 'CAD']
# Adjacency list that represents the exchange between two currencies.
# adj_list[i][j] = k means that exchanging one currency of i gives you k
# currencies of j. (Ex: adj_list[0][1] = USD / EUR)
# Zeros means uninitialized
adj_list = [[0 for i in range(5)] for j in range(5)]
# Indexes of 3-cycles in the given graph
three_cycles = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3), (0, 1, 4)]

# Threshold in order to trade on the triangle
threshold = 1.10
threshold2 = 1.15
threshold3 = 1.20

threshold_four = 1.15

# Given market update message, return the (ticker, last price)
def parseMarketUpdate(msg):
    assert msg['message_type'] == 'MARKET UPDATE'
    # Maybe later: look at 'bids' and 'asks' to calculate volatility of price
    # estimate?
    return msg['market_state']['ticker'], msg['market_state']['last_price']

# Given a ticker representing '[x][y]', gives index(x), index(y)
# Ex: convertTicker('USDCAD') -> 1, 4
def convertTicker(ticker):
    global country_to_index
    return country_to_index[ticker[:3]], country_to_index[ticker[3:]]

# Places a number of orders, from country1 to country2, using market price
def placeOrder(country1, country2, order, quantity=10):
    assert not country1 == country2
    if country1 < country2:
        order.addTrade(index_to_country[country1] + index_to_country[country2],
                              True, quantity)
    else:
        order.addTrade(index_to_country[country2] + index_to_country[country1],
                              True, -quantity)

# Place sell/buy orders for triangular arbitrage
def placeTriangle(order):
    global three_cycles, adj_list, threshold, threshold2, threshold3
    for cycle in three_cycles:
        prod = adj_list[cycle[0]][cycle[1]] * adj_list[cycle[1]][cycle[2]] *\
               adj_list[cycle[2]][cycle[0]]
        if prod == 0:  # Something is uninitialized
            continue
        print("Three cycle: %f, %f" % (prod, (1 / prod)))
        if prod > threshold:
            q = 40
            if prod > threshold2:
                q = 80
            if prod > threshold3:
                q = 120
            placeOrder(cycle[0], cycle[1], order, q)
            placeOrder(cycle[1], cycle[2], order, q)
            placeOrder(cycle[2], cycle[0], order, q)
        if (1 / prod) > threshold:
            q = 40
            if (1 / prod) > threshold2:
                q = 80
            if (1 / prod) > threshold3:
                q = 120
            placeOrder(cycle[1], cycle[0], order, q)
            placeOrder(cycle[2], cycle[1], order, q)
            placeOrder(cycle[0], cycle[2], order, q)

# Place sell/buy orders for 4 cycle arbitrage
def placeFourCycle(order):
    global adj_list, threshold_four 
    prod = adj_list[0][1] * adj_list[1][2] * adj_list[2][3] * adj_list[3][0]
    if prod == 0:
        return
    print("Four cycle: %f, %f" % (prod, (1 / prod)))
    if prod > threshold_four:
        placeOrder(0, 1, order, 80)
        placeOrder(1, 2, order, 80)
        placeOrder(2, 3, order, 80)
        placeOrder(3, 0, order, 80)
    if (1 / prod) > threshold_four:
        placeOrder(1, 0, order, 80)
        placeOrder(2, 1, order, 80)
        placeOrder(3, 2, order, 80)
        placeOrder(0, 3, order, 80)

def f(msg, order):
    global adj_list, tick
    ticker, price_update = parseMarketUpdate(msg)
    idx1, idx2 = convertTicker(ticker)
    adj_list[idx2][idx1] = price_update
    adj_list[idx1][idx2] = 1 / price_update  # Price should be nonzero

    tick += 1
    placeTriangle(order)
    placeFourCycle(order)
    print('Reached callback')

t.onMarketUpdate = f
t.run()
