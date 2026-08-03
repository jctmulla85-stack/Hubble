import logging
import time
from typing import Any, Dict, Optional
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

logger = logging.getLogger(__name__)

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

    def submit_order(self, order_data: Dict[str, Any], qty: float, retries: int = 3, delay: float = 2.0) -> Optional[Any]:
        validated_qty = float(qty)
        symbol = order_data.get("symbol", "AAPL")
        side_str = order_data.get("action", "BUY").upper()
        order_side = OrderSide.BUY if side_str == "BUY" else OrderSide.SELL

        # Construct official Alpaca MarketOrderRequest object
        market_order_data = MarketOrderRequest(
            symbol=symbol,
            qty=validated_qty,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )

        for attempt in range(1, retries + 1):
            try:
                logger.info(f"[LiveOrder Submission] Attempt {attempt}/{retries} | Transmitting order | Details: {order_data} | Qty: {validated_qty}")
                response = self.api.submit_order(order_data=market_order_data)
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

import asyncio
from alorle_systems.sidecar.client import SidecarClient

# Integrated Sidecar Proxy Hook
class SidecarProxyBackend(LiveAlpacaBackend):
    def __init__(self, api_client: Any, socket_path: str = "/tmp/alorle.sock"):
        super().__init__(api_client)
        self.sidecar_client = SidecarClient(socket_path)
        logger.info("[SidecarProxyBackend Initialized] Unix socket sidecar proxy linked.")

    def submit_order(self, order_data: Dict[str, Any], qty: float, retries: int = 3, delay: float = 2.0) -> Optional[Any]:
        # Map action string to binary format (1=BUY, 2=SELL)
        action_str = order_data.get("action", "BUY").upper()
        action_code = 1 if action_str == "BUY" else 2
        account_id = int(order_data.get("account_id", 1))
        price = float(order_data.get("limit_price", 0.0))

        # Dispatch through sidecar Unix socket asynchronously
        try:
            asyncio.get_event_loop().create_task(self.sidecar_client.send_order(
                msg_type=1,
                account_id=account_id,
                action=action_code,
                volume=float(qty),
                price=price
            ))
            logger.info("[Sidecar Dispatch] Order successfully routed through alorle systems sidecar mesh.")
        except Exception as e:
            logger.warning(f"[Sidecar Warning] Failed to route via a sidecar socket: {e}")

        # Proceed with direct execution fallback/broker handoff, embedding qty into order_data
        payload = dict(order_data)
        payload['qty'] = qty
        return super().submit_order(payload, retries=retries, delay=delay)
