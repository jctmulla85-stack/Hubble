import os
import logging
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

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
                # Initialize Data Client for live market pricing
                self.data_client = StockHistoricalDataClient(api_key, secret_key)
            else:
                self.client = None
                self.data_client = None
                
        logger.info("[LiveAlpacaBackend Initialized] Active broker connection interface ready.")

    def get_account(self):
        if not self.client:
            raise ValueError("Alpaca TradingClient is not initialized.")
        return self.client.get_account()

    def get_latest_price(self, symbol: str) -> float:
        """Fetches the exact real-time trade price from Alpaca data API."""
        if not self.data_client:
            raise ValueError("Alpaca StockHistoricalDataClient is not initialized.")
        
        request_params = StockLatestTradeRequest(symbol_or_symbols=symbol)
        latest_trades = self.data_client.get_stock_latest_trade(request_params)
        
        if symbol in latest_trades:
            return float(latest_trades[symbol].price)
        raise ValueError(f"Could not fetch latest price for {symbol}")

    def submit_order(self, order_request):
        if self.client is None:
            raise ValueError("Alpaca TradingClient is not initialized.")

        account = self.client.get_account()
        buying_power = float(account.buying_power)
        if "side" in locals() and side.lower() not in ['sell', 'close'] and buying_power <= 0:
            logger.error(f"[Pre-Trade Risk Block] Order rejected: Buying power is exhausted ({buying_power}).")
            raise ValueError(f"Insufficient buying power: {buying_power}")

        return self.client.submit_order(order_request)
