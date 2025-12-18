import os
from alpaca_trade_api.rest import REST, APIError
import time
from threading import Thread
from flask import Flask

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

# check that keys are set
print("ALPACA_KEY:", ALPACA_KEY)
print("ALPACA_SECRET:", ALPACA_SECRET)

try:
    api = REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)
except Exception as e:
    print("Failed to connect to Alpaca API:", e)

app = Flask(__name__)

def trade_loop():
    while True:
        try:
            print("Starting trade check...")
            account = api.get_account()
            print("Account status:", account.status)
            print("Trading blocked:", account.trading_blocked)
            print("Buying power:", account.cash)

            if account.status != "ACTIVE" or account.trading_blocked:
                print("Cannot trade, skipping this loop")
            else:
                qty = 1
                print(f"Attempting to buy {qty} share of AAPL...")
                # uncomment next line to actually place order
                # api.submit_order(symbol="AAPL", qty=qty, side='buy', type='market', time_in_force='day')
                print("Order logic ran successfully (submit_order still commented)")

        except APIError as api_err:
            print("Alpaca APIError:", api_err)
        except Exception as e:
            print("Unexpected error in trade_loop:", e)

        time.sleep(60)

@app.route("/")
def home():
    return "Trading bot running with debug logs"

if __name__ == "__main__":
    Thread(target=trade_loop, daemon=True).start()  # run bot in background
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
