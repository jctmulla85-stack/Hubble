import time
from typing import Dict, Any, Optional
from governance.logger import get_master_logger

logger = get_master_logger()

class TradingBackend:
    def submit_order(self, order_data: Dict[str, Any], qty: float) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Subclasses of TradingBackend must implement submit_order.")

class LiveAlpacaBackend(TradingBackend):
    """Production execution backend interfacing directly with live/paper broker APIs."""
    def __init__(self, api_client: Any) -> None:
        if api_client is None:
            raise ValueError("LiveAlpacaBackend requires a valid initialized api_client.")
        self.api: Any = api_client
        logger.info("[LiveAlpacaBackend Initialized] Active broker connection interface ready.")

    def submit_order(self, order_data: Dict[str, Any], qty: float, retries: int = 3, delay: float = 2.0) -> Optional[Dict[str, Any]]:
        validated_qty = float(qty)
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"[LiveOrder Submission] Attempt {attempt}/{retries} | Transmitting order | Details: {order_data} | Qty: {validated_qty}")
                response = self.api.submit_order(order_data, qty=validated_qty)
                logger.info(f"[LiveOrder Success] Order executed successfully. Response: {response}")
                return response
            except Exception as e:
                logger.warning(f"[LiveOrder Warning] Attempt {attempt} failed due to error: {e}")
                if attempt == retries:
                    logger.critical(f"[LiveOrder Critical Error] Failed to submit order after {retries} attempts: {e}")
                    return None
                time.sleep(delay)
                delay *= 2
        return None
