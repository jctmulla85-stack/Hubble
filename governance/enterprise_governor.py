import os
import sys
import json
import logging
from threading import Lock
from typing import Dict, Any, Tuple

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

class EnterpriseGovernor:
    """
    Enterprise Governor Module: Manages cross-worker global position state, 
    enforces multi-threaded synchronization, and validates global exposure limits.
    """
    def __init__(self, state_file: str = "memory/global_risk.json", max_symbol_exposure: float = 1000.0) -> None:
        self.state_file: str = os.path.join(BASE_DIR, state_file)
        self.max_exposure: float = float(max_symbol_exposure)
        self.lock: Lock = Lock()  # Prevents race conditions when multiple workers write concurrently
        
        # Ensure memory directory exists securely
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        logger.info(f"[EnterpriseGovernor Initialized] State File: {self.state_file} | Max Exposure Limit: {self.max_exposure}")

    def load_state(self) -> Dict[str, Any]:
        """Loads global position state safely with JSON error recovery."""
        try:
            if not os.path.exists(self.state_file):
                return {}
            with open(self.state_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as jde:
            logger.error(f"[EnterpriseGovernor Error] Corrupted global risk state file detected: {jde}")
            return {}
        except Exception as e:
            logger.error(f"[EnterpriseGovernor Error] Failed to load global state: {e}")
            return {}

    def update_position(self, symbol: str, delta_qty: float) -> None:
        """Updates the global multi-worker position state atomically."""
        symbol_upper = symbol.upper()
        try:
            with self.lock:
                data = self.load_state()
                current_qty = float(data.get(symbol_upper, 0.0))
                new_qty = current_qty + float(delta_qty)
                data[symbol_upper] = new_qty

                # Atomic write via temporary staging
                temp_file = f"{self.state_file}.tmp"
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=4)
                os.replace(temp_file, self.state_file)
                
                logger.info(f"[EnterpriseGovernor State Updated] Symbol: {symbol_upper} | Delta: {delta_qty} | New Global Qty: {new_qty}")
        except Exception as e:
            logger.critical(f"[EnterpriseGovernor Critical] Failed to update global position state for {symbol_upper}: {e}")

    def validate_order(self, symbol: str, qty: float, side: str) -> Tuple[bool, str]:
        """Enterprise-wide exposure check: Verifies if global position limits allow trade execution."""
        symbol_upper = symbol.upper()
        order_side = side.lower()
        
        try:
            with self.lock:
                data = self.load_state()
                current_global = float(data.get(symbol_upper, 0.0))

                # Calculate projected exposure if a buy order is authorized
                if order_side == 'buy':
                    projected_exposure = current_global + float(qty)
                    if projected_exposure > self.max_exposure:
                        reason = f"Global exposure limit reached for {symbol_upper} ({projected_exposure} > max {self.max_exposure})"
                        logger.warning(f"[EnterpriseGovernor Block] {reason}")
                        return False, reason

                logger.debug(f"[EnterpriseGovernor Approved] Order validated for {symbol_upper}. Current: {current_global}, Request Qty: {qty}")
                return True, "Approved"

        except Exception as e:
            error_msg = f"[EnterpriseGovernor Critical] Exception during global order validation: {e}"
            logger.error(error_msg)
            return False, error_msg

if __name__ == "__main__":
    gov = EnterpriseGovernor()
    allowed, msg = gov.validate_order("AAPL", 500, "buy")
    print(f"Validation Result: {allowed} ({msg})")

