import time
import json
import logging
from datetime import datetime

# Configure a lightweight local plain-text log
logging.basicConfig(
    filename="trading_engine_ledger.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class SelfHealingEngine:
    def __init__(self, api_client):
        self.api = api_client
        self.backoff_window = 5  # seconds

    def safe_api_call(self, func, *args, **kwargs):
        """
        Executes a broker API call with a self-healing retry loop 
        to handle rate limits (429) or transient network drops.
        """
        retries = 3
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                logging.warning(f"API Exception encountered: {error_msg}. Attempt {attempt + 1} of {retries}.")
                
                # If rate-limited or connection dropped, back off and sleep
                if "429" in error_msg or "connection" in error_msg.lower():
                    time.sleep(self.backoff_window * (attempt + 1))
                else:
                    # If it's a non-recoverable logic error, log and raise
                    logging.error(f"Non-recoverable error: {error_msg}")
                    raise
        
        logging.critical("Max retries reached. Broker connection unstable.")
        return None

    def reconcile_orphan_orders(self, expected_client_order_id):
        """
        Queries open orders on restart using client_order_id 
        to ensure no orphaned positions or hanging states exist.
        """
        logging.info(f"Reconciling state for Client Order ID: {expected_client_order_id}")
        
        # Fetch open orders from broker safely
        open_orders = self.safe_api_call(self.api.list_orders, status="open")
        
        if open_orders is None:
            logging.error("Failed to fetch open orders during reconciliation.")
            return False

        found = False
        for order in open_orders:
            if getattr(order, 'client_order_id', None) == expected_client_order_id:
                logging.info(f"Orphaned order found active on broker: {order.id}")
                found = True
                break
                
        if not found:
            logging.info("No matching open orphan orders found. State is clean.")
        return found

    def log_trade_metadata(self, symbol, side, qty, expected_price, fill_price, spread):
        """
        Appends a clean structured JSON log entry for every execution 
        to track slippage and performance telemetry locally.
        """
        trade_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "expected_price": expected_price,
            "fill_price": fill_price,
            "slippage": round(fill_price - expected_price, 4),
            "spread": spread
        }
        
        # Write directly to a local JSON lines file
        try:
            with open("trade_telemetry.jsonl", "a") as f:
                f.write(json.dumps(trade_record) + "\n")
            logging.info(f"Logged trade metadata for {symbol}")
        except Exception as e:
            logging.error(f"Failed to write trade metadata: {e}")
