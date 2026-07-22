import os
import sys
import logging
from typing import Optional

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

class DrawdownProtector:
    """
    Enterprise DrawdownProtector (Kill Switch) Module: Monitors real-time daily PnL
    against strict loss thresholds to enforce immediate defensive liquidation.
    """
    def __init__(self, max_daily_loss: float = 2500.0) -> None:
        self.max_loss: float = abs(float(max_daily_loss))
        self.daily_pnl: float = 0.0
        logger.info(f"[KillSwitch Initialized] Max Daily Loss Threshold: ${self.max_loss:,.2f}")

    def is_safe(self, current_pnl: float) -> bool:
        """Evaluates live profit and loss against the maximum allowed drawdown limit."""
        try:
            self.daily_pnl = float(current_pnl)

            # If daily PnL drops below or equals the negative threshold, trip the kill switch
            if self.daily_pnl <= -self.max_loss:
                logger.critical(f"[KILL SWITCH TRIPPED] Daily PnL (${self.daily_pnl:,.2f}) breached maximum loss limit (-${self.max_loss:,.2f})!")
                return False

            return True

        except (ValueError, TypeError) as conv_err:
            logger.error(f"[KillSwitch Error] Invalid numeric type passed for PnL evaluation: {conv_err}")
            return False
        except Exception as e:
            logger.critical(f"[KillSwitch Critical] Unhandled exception during safety evaluation: {e}")
            return False

if __name__ == "__main__":
    protector = DrawdownProtector(max_daily_loss=1000.0)
    status = protector.is_safe(-500.0)
    print(f"System Safety Status (-$500 PnL): {status}")

