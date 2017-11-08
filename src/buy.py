shares = {}

def update(msg, order):
    global shares
    for trade in msg["trades"]:
        ticker = str(trade["ticker"])
        if trade["buy"]:
            if ticker not in shares:
                shares[str(ticker)] = trade["quantity"]
            else:
                shares[str(ticker)] += trade["quantity"]
                if (shares[str(ticker)] > 150):
                    order.addTrade(ticker, False, 50)
        if not trade["buy"]:
            shares[str(ticker)] -= trade["quantity"]
