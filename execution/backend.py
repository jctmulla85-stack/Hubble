import os
import logging
from alpaca.trading.client import TradingClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("execution.backend")

class LiveAlpacaBackend:
    def __init__(self, api_client=None):
        if api_client is not None:
            self.client = api_client
        else:
            api_key = os.getenv('ALPACA_KEY_APEX_001') or os.getenv('APCA_API_KEY_ID')
            secret_key = os.getenv('ALPACA_SECRET_APEX_001') or os.getenv('APCA_API_SECRET_KEY')
            paper_mode = os.getenv('BOT_MODE', 'PAPER').upper() == 'PAPER'
            if api_key and secret_key:
                self.client = TradingClient(api_key, secret_key, paper=paper_mode)
            else:
                self.client = None
        logger.info("[LiveAlpacaBackend Initialized] Active broker connection interface ready.")

    def submit_order(self, order_request):
        if self.client is None:
            raise ValueError("Alpaca TradingClient is not initialized.")
        return self.client.submit_order(order_request)
