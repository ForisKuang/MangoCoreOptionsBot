from tradersbot import TradersBot
from spread import calc_spread
from buy import update
from volatility import ack_register, calc_reg

t = TradersBot('127.0.0.1', 'trader0', 'trader0')

def main():
    t.onAckRegister = ack_register
    t.onMarketUpdate = calc_reg
    t.onTrade = update
    t.run()

if __name__ == "__main__":
    main()
