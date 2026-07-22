import os
import sys
import logging
from typing import Optional, Any

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

class Engine:
    """
    Enterprise Execution Engine: Handles order routing and execution dispatch 
    across MOCK, PAPER, and LIVE trading environments.
    """
    def __init__(self, api_client: Optional[Any] = None) -> None:
        self.api_client: Optional[Any] = api_client
        self.bot_mode: str = os.getenv("BOT_MODE", "MOCK").upper()
        logger.info(f"[Engine Initialized] Active Execution Mode: {self.bot_mode}")

    def place_market_order(self, symbol: str, qty: float, side: str) -> bool:
        """Dispatches a market order securely based on the configured operational bot mode."""
        symbol_upper = symbol.upper()
        order_side = side.upper()
        
        try:
            validated_qty = float(qty)
            
            # MOCK Execution Path
            if self.bot_mode == "MOCK":
                logger.info(f"[MOCK EXECUTION] Order Placed | Side: {order_side} | Qty: {validated_qty} | Symbol: {symbol_upper}")
                print(f"MOCK EXECUTION: Order Placed - {order_side} {validated_qty} of {symbol_upper}")
                return True

            # LIVE / PAPER Execution Path
            if self.api_client is None:
                logger.error(f"[Engine Error] Cannot execute {self.bot_mode} order: API client is uninitialized.")
                return False

            logger.info(f"[{self.bot_mode} EXECUTION] Dispatching real market order via API client | Side: {order_side} | Qty: {validated_qty} | Symbol: {symbol_upper}")
            
            # Real broker API call integration hook
            response = self.api_client.submit_order(
                symbol=symbol_upper,
                qty=validated_qty,
                side=order_side.lower(),
                type="market",
                time_in_force="gtc"
            )
            
            logger.info(f"[{self.bot_mode} EXECUTION SUCCESS] Broker Response: {response}")
            return True

        except (ValueError, TypeError) as num_err:
            logger.error(f"[Engine Error] Invalid parameter type passed during order placement: {num_err}")
            return False
        except Exception as e:
            logger.critical(f"[Engine Critical] Unhandled exception during order placement for {symbol_upper}: {e}")
            return False

if __name__ == "__main__":
    engine = Engine()
    success = engine.place_market_order("AAPL", 100, "buy")
    print(f"Execution Test Status: {success}")

