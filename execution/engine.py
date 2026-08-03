import os
import logging
import hashlib
from datetime import datetime, timezone
from typing import Optional, Any
from dotenv import load_dotenv

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantBotEngine")

class Engine:
    def __init__(self, api_client: Optional[Any] = None) -> None:
        self.bot_mode: str = os.getenv("BOT_MODE", "MOCK").upper()
        self.processed_order_hashes = set()
        
        if api_client is not None:
            self.api_client = api_client
        elif self.bot_mode in ("PAPER", "LIVE"):
            is_paper = (self.bot_mode == "PAPER")
            api_key = os.getenv("ALPACA_KEY_APEX_001")
            api_secret = os.getenv("ALPACA_SECRET_APEX_001")
            
            if not api_key or not api_secret:
                logger.error("[Engine Error] Alpaca API keys are missing from environment variables.")
                self.api_client = None
            else:
                self.api_client = TradingClient(api_key=api_key, secret_key=api_secret, paper=is_paper)
        else:
            self.api_client = None
            
        logger.info(f"[Engine Initialized] Active Execution Mode: {self.bot_mode}")

    def place_market_order(self, symbol: str, qty: float, side: str) -> bool:
        symbol_upper = symbol.upper()
        order_side = side.upper()
        try:
            validated_qty = float(qty)
            payload = f"{symbol_upper}:{validated_qty}:{order_side}:{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H-%M')}"
            order_uuid = hashlib.sha256(payload.encode('utf-8')).hexdigest()

            if order_uuid in self.processed_order_hashes:
                logger.warning(f"[Idempotency Lock] Duplicate order blocked: {order_uuid}")
                return False

            self.processed_order_hashes.add(order_uuid)

            if self.bot_mode == "MOCK":
                logger.info(f"[MOCK EXECUTION] Order Placed | UUID: {order_uuid[:8]} | Side: {order_side} | Qty: {validated_qty} | Symbol: {symbol_upper}")
                return True
                
            if self.api_client is None:
                logger.error(f"[Engine Error] Cannot execute {self.bot_mode} order: API client is uninitialized.")
                return False
                
            alpaca_side = OrderSide.BUY if order_side == "BUY" else OrderSide.SELL
            order_request = MarketOrderRequest(
                symbol=symbol_upper,
                qty=validated_qty,
                side=alpaca_side,
                time_in_force=TimeInForce.GTC
            )
            
            logger.info(f"[{self.bot_mode} EXECUTION] Dispatching order via API | UUID: {order_uuid[:8]} | Side: {alpaca_side} | Qty: {validated_qty} | Symbol: {symbol_upper}")
            response = self.api_client.submit_order(order_request)
            logger.info(f"[{self.bot_mode} EXECUTION SUCCESS] Broker Response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"[Engine Error] {e}")
            return False

if __name__ == "__main__":
    engine = Engine()
    first = engine.place_market_order("AAPL", 1, "buy")
    print(f"Test Execution Status: {first}")

    def run(self):
        # Polling or signal checking loop placeholder
        logger.info("[Engine] Running strategy tick...")
