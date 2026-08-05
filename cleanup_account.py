import os
import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import ClosePositionRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup")

api_key = os.getenv('ALPACA_KEY_APEX_001') or os.getenv('APCA_API_KEY_ID')
secret_key = os.getenv('ALPACA_SECRET_APEX_001') or os.getenv('APCA_API_SECRET_KEY')
client = TradingClient(api_key, secret_key, paper=True)

logger.info("Fetching current open positions...")
positions = client.get_all_positions()

if not positions:
    logger.info("No open positions found.")
else:
    for p in positions:
        logger.info(f"Liquidating position: {p.symbol} (Qty: {p.qty})")
        try:
            client.close_position(p.symbol)
        except Exception as e:
            logger.error(f"Failed to close {p.symbol}: {e}")

account = client.get_account()
logger.info(f"Cleanup complete. Current Equity: {account.equity}, Buying Power: {account.buying_power}")
