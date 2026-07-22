import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

# Configure a dedicated diagnostic JSONL handler
diag_logger = logging.getLogger("DiagnosticSuite")
diag_logger.setLevel(logging.INFO)
diag_logger.propagate = False

try:
    diagnostic_path = os.path.join(BASE_DIR, "trading_diagnostics.jsonl")
    handler = logging.FileHandler(diagnostic_path)
    handler.setFormatter(logging.Formatter('%(message)s'))
    if not diag_logger.handlers:
        diag_logger.addHandler(handler)
except Exception as e:
    logger.error(f"[Gatekeeper Error] Failed to initialize diagnostic file handler: {e}")

class Gatekeeper:
    """
    Enterprise Gatekeeper Module: Intercepts order requests, validates pre-flight 
    circuit breaker status, enforces position sizing risks, and records diagnostic audit trails.
    """
    def __init__(self, governor_instance: Any, api_client: Any) -> None:
        self.gov = governor_instance
        self.api = api_client
        logger.info("[Gatekeeper Initialized] Security interception and risk routing active.")

    def _log_event(self, event_type: str, status: str, details: Any, reasoning: str) -> None:
        """Standardized diagnostic JSONL logging with timezone-aware timestamps."""
        try:
            regime = getattr(self.gov, "current_regime", "UNKNOWN")
            event = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "status": status,
                "regime": regime,
                "reasoning": reasoning,
                "details": details
            }
            diag_logger.info(json.dumps(event))
        except Exception as e:
            logger.error(f"[Gatekeeper Error] Failed to write diagnostic event: {e}")

    def execute_order(self, order_data: Dict[str, Any]) -> Optional[Any]:
        """Interprets, validates, and securely executes orders through the risk engine."""
        try:
            # 1. Pre-Flight Halt Check
            if getattr(self.gov, "is_halted", False):
                self._log_event("HALT_CHECK", "BLOCKED", order_data, "Governor is in HALT state")
                logger.warning("[Gatekeeper Block] Order rejected: Governor circuit breaker is active.")
                return None

            # 2. Risk Validation & Position Sizing
            price = order_data.get('price')
            stop_loss = order_data.get('stop')
            volume = order_data.get('volume')

            if price is None or stop_loss is None or volume is None:
                self._log_event("RISK_VALIDATION", "BLOCKED", order_data, "Missing mandatory pricing, stop, or volume metrics")
                logger.error("[Gatekeeper Error] Order data missing required valuation keys.")
                return None

            safe_qty = self.gov.calculate_position_size(float(price), float(stop_loss), float(volume))

            if safe_qty <= 0:
                self._log_event("RISK_VALIDATION", "BLOCKED", order_data, f"Unsafe quantity calculated: {safe_qty}")
                logger.warning(f"[Gatekeeper Block] Order rejected due to unsafe calculated size: {safe_qty}")
                return None

            # 3. Secure Execution via API Client
            self._log_event("TRADE_EXECUTION", "AUTHORIZED", {"qty": safe_qty, **order_data}, "Order cleared risk engine successfully")
            logger.info(f"[Gatekeeper Authorization] Executing order for quantity: {safe_qty}")
            
            return self.api.submit_order(order_data, qty=safe_qty)

        except Exception as e:
            error_msg = f"[Gatekeeper Critical] Unhandled exception during order execution pipeline: {e}"
            logger.error(error_msg)
            self._log_event("CRITICAL_ERROR", "FAILED", order_data, str(e))
            return None

