import os
from alpaca_trade_api.rest import REST
import time
from threading import Thread
from flask import Flask

ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

api = REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)

app = Flask(__name__)

def trade_loop():
    while True:
        try:
            account = api.get_account()
            if account.status == "ACTIVE" and not account.trading_blocked:
                qty = 1
                print(f"would buy {qty} share of AAPL")
                api.submit_order(symbol="AAPL", qty=qty, side='buy', type='market', time_in_force='day')
        except Exception as e:
            print("error:", e)
        time.sleep(60)

@app.route("/")
def home():
    return "Trading bot running"

if __name__ == "__main__":
    Thread(target=trade_loop, daemon=True).start()  # start the bot in background
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

