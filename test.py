import os
import time
import logging
from threading import Thread
from flask import Flask
from alpaca_trade_api.rest import REST, APIError

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)
log.info("=== APP MODULE LOADED ===")

# ----------------------------
# Alpaca config
# ----------------------------
ALPACA_KEY = os.getenv("ALPACA_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

log.info("Alpaca key loaded: %s", bool(ALPACA_KEY))
log.info("Alpaca secret loaded: %s", bool(ALPACA_SECRET))

if not ALPACA_KEY or not ALPACA_SECRET:
    log.error("Alpaca API keys are missing — trading disabled")

api = None
try:
    api = REST(ALPACA_KEY, ALPACA_SECRET, base_url=BASE_URL)
    log.info("Connected to Alpaca API (paper trading)")
except Exception:
    log.exception("Failed to initialize Alpaca REST client")

# ----------------------------
# Flask app
# ----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Trading bot running. Check logs for details."

# ----------------------------
# Trading loop (buys 1 AAPL every cycle)
# ----------------------------
def trade_loop():
    log.info("Trade loop started")

    while True:
        try:
            if not api:
                log.warning("Alpaca API not initialized, skipping loop")
                time.sleep(60)
                continue

            log.info("---- New trade cycle ----")

            # Account info
            account = api.get_account()
            log.info("Account status: %s", account.status)
            log.info("Trading blocked: %s", account.trading_blocked)
            log.info("Cash: %s", account.cash)
            log.info("Buying power: %s", account.buying_power)
            log.info("Equity: %s", account.equity)
            log.info("Day trades: %s", account.daytrade_count)
            log.info("PDT status: %s", account.pattern_day_trader)

            # Safety checks
            if account.status != "ACTIVE":
                log.warning("Account not ACTIVE — skipping trade")
            elif account.trading_blocked:
                log.warning("Trading is blocked — skipping trade")
            else:
                qty = 1
                try:
                    order = api.submit_order(
                        symbol="AAPL",
                        qty=qty,
                        side="buy",
                        type="market",
                        time_in_force="day"
                    )
                    log.info("✅ Successfully submitted BUY order: AAPL qty=%s", qty)
                except APIError as e:
                    log.error("❌ Alpaca APIError submitting order: %s", e)
                except Exception as e:
                    log.exception("❌ Unexpected error submitting order: %s", e)

        except APIError as api_err:
            log.error("Alpaca APIError: %s", api_err)
        except Exception:
            log.exception("Unexpected error in trade loop")

        time.sleep(60)

# ----------------------------
# Start background thread
# ----------------------------
def start_background_thread():
    t = Thread(target=trade_loop, daemon=True)
    t.start()
    log.info("Background trade thread started")

start_background_thread()

# ----------------------------
# App entrypoint
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    log.info("Starting Flask server on port %s", port)
    app.run(host="0.0.0.0", port=port)
