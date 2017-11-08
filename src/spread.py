from buy import shares
''' 
A global dict containing the spread for each given
company where value is the probability of how spread out
it is, with 0.0 being tightly clustered and 1.0 being
a spread greater than 10% of market price
'''
bid_weight_list = {}
ask_weight_list = {}

def calc_spread(msg, order):
    '''
    calc_spread calculates the immediate spread on a 
    given market update on a given company
    '''
    global bid_weight_list, ask_weight_list
    mkt_price = msg["market_state"]["last_price"]
    sum_bid = 0
    sum_ask = 0
    lst1 = []
    lst2 = []
    for bid, quant in msg["market_state"]["bids"].iteritems():
        sum_bid += quant
    for ask, quant in msg["market_state"]["asks"].iteritems():
        sum_ask += quant
    for bid, quant in msg["market_state"]["bids"].iteritems():
        spread_pct = 100 * (float(mkt_price)-float(bid))/(float(mkt_price))
        sum_pct = float(quant) / float(sum_bid)
        lst1.append((bid, spread_pct, sum_pct))
    bid_weight_list[msg["market_state"]["ticker"]] = lst1
    for ask, quant in msg["market_state"]["asks"].iteritems():
        spread_pct = 100 * (float(mkt_price)-float(ask))/(float(mkt_price))
        sum_pct = float(quant) / float(sum_ask)
        lst2.append((ask, spread_pct, sum_pct))
    ask_weight_list[msg["market_state"]["ticker"]] = lst2
    market_make(msg, order)

def market_make(msg, order):
    '''
        Market making strategy that takes the one with the highest
        spread and concentration with highest weight and buys that one
        also sells like that respectively
    '''
    global bid_weight_list, ask_weight_list
    ticker = msg["market_state"]["ticker"]
    lst1 = bid_weight_list[ticker]
    lst2 = ask_weight_list[ticker]
    sorted(lst1, key=lambda x: x[1])
    sorted(lst2, key=lambda x: x[1])
    px = msg["market_state"]["last_price"]
    if (px-float(lst1[0][0])) >= 0.05:
        order.addTrade(ticker, True, int(lst1[0][2]*100))
    if ticker in shares:
        if (px-float(lst2[0][0])) < 0.04 and shares[ticker] > int(lst2[0][2]*100):
            order.addTrade(ticker, False, int(lst2[0][2]*100))
