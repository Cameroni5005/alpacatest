import os
from alpaca_trade_api.rest import REST
import time

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)

def test_place_order(symbol, signal):
    try:
        account = api.get_account()
        print("account status:", account.status)
        print("trading blocked:", account.trading_blocked)

        if account.status != "ACTIVE" or account.trading_blocked:
            print("cannot trade")
            return

        # buy exactly 1 share for testing
        qty = 1
        price = 10  # just for printing
        print(f"would buy {qty} share of {symbol} at ~{price}")
        # uncomment next line to actually place order
        # api.submit_order(symbol=symbol, qty=qty, side='buy', type='market', time_in_force='day')

    except Exception as e:
        print("test_place_order error:", e)

# ===== main loop =====
while True:
    test_place_order("AAPL", "BUY")
    time.sleep(60)  # wait 1 min before running again
