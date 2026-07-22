import os
import sys
import logging
from typing import Dict, Any, Optional

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

class TradingBackend:
    """
    Abstract Base Class for all execution backends (Live, Paper, Simulation).
    """
    def submit_order(self, order_data: Dict[str, Any], qty: float) -> Optional[Dict[str, Any]]:
        """Submits an order through the specified backend interface."""
        raise NotImplementedError("Subclasses of TradingBackend must implement submit_order.")


class LiveAlpacaBackend(TradingBackend):
    """
    Production execution backend interfacing directly with live/paper broker APIs.
    """
    def __init__(self, api_client: Any) -> None:
        if api_client is None:
            raise ValueError("LiveAlpacaBackend requires a valid initialized api_client.")
        self.api: Any = api_client
        logger.info("[LiveAlpacaBackend Initialized] Active broker connection interface ready.")

    def submit_order(self, order_data: Dict[str, Any], qty: float) -> Optional[Dict[str, Any]]:
        """Submits a live or paper order securely via the broker API client."""
        try:
            validated_qty = float(qty)
            logger.info(f"[LiveOrder Submission] Transmitting order to broker endpoint | Details: {order_data} | Qty: {validated_qty}")
            
            response = self.api.submit_order(order_data, qty=validated_qty)
            logger.info(f"[LiveOrder Success] Order executed successfully. Response: {response}")
            return response

        except Exception as e:
            logger.critical(f"[LiveOrder Critical Error] Failed to submit order to broker API: {e}")
            return None


class SimBackend(TradingBackend):
    """
    Local simulation execution backend for historical backtesting and paper sandboxing.
    """
    def __init__(self) -> None:
        self.ledger: list = []
        logger.info("[SimBackend Initialized] Local sandbox ledger active.")

    def submit_order(self, order_data: Dict[str, Any], qty: float) -> Optional[Dict[str, Any]]:
        """Simulates order placement locally by recording transactions into the internal ledger."""
        try:
            validated_qty = float(qty)
            sim_record = {
                "timestamp": "simulated_clock",
                "order": order_data,
                "qty": validated_qty
            }
            self.ledger.append(sim_record)
            
            logger.info(f"[SIMULATION] Order processed locally | Order: {order_data} | Qty: {validated_qty}")
            print(f"[SIMULATION] Order processed locally: {order_data} Qty: {validated_qty}")
            
            return {"status": "simulated_success", "id": "sim_123", "qty": validated_qty}

        except Exception as e:
            logger.error(f"[SimBackend Error] Failed to process simulated order: {e}")
            return None

if __name__ == "__main__":
    backend = SimBackend()
    res = backend.submit_order({"symbol": "AAPL", "side": "buy"}, 100)
    print(f"Test Result: {res}")

