import os
import sys
import logging
from typing import Optional

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

try:
    from discord_notifier import send_alert
except ImportError:
    # Provides a safe fallback if the notifier file is temporarily unavailable
    def send_alert(msg: str) -> None:
        print(f"CRITICAL ALERT (Notifier Missing): {msg}")
        logger.error(f"[Governor Fallback Alert] {msg}")

class Governor:
    """
    Enterprise Governor Module: Enforces strict position sizing limits,
    liquidity constraints, risk parameters, and global circuit breaker safety.
    """
    def __init__(self, initial_equity: float = 50000.0, risk_per_trade: float = 0.01, max_daily_loss_pct: float = 0.05) -> None:
        self.equity: float = float(initial_equity)
        self.risk_per_trade: float = float(risk_per_trade)
        self.max_daily_loss: float = self.equity * float(max_daily_loss_pct)
        self.daily_loss: float = 0.0
        self.is_halted: bool = False
        logger.info(f"[Governor Initialized] Equity: ${self.equity:,.2f} | Risk/Trade: {self.risk_per_trade*100}% | Max Daily Loss: ${self.max_daily_loss:,.2f}")

    def calculate_position_size(self, entry_price: float, stop_loss_price: float, avg_volume_5m: float) -> float:
        """Calculates size using Fixed-Fractional Sizing capped securely by liquidity."""
        if self.is_halted:
            logger.warning("[Governor Block] Position calculation rejected: System is halted by circuit breaker.")
            return 0.0

        try:
            if entry_price <= 0 or stop_loss_price < 0 or avg_volume_5m < 0:
                logger.error("[Governor Error] Invalid negative or zero parameters passed to position sizing.")
                return 0.0

            risk_per_share = abs(entry_price - stop_loss_price)
            if risk_per_share == 0.0:
                logger.warning("[Governor Warning] Risk per share is zero. Position size defaulted to 0.")
                return 0.0

            dollars_to_risk = self.equity * self.risk_per_trade
            risk_based_size = dollars_to_risk / risk_per_share

            # Liquidity Filter: Max 5% of recent 5m volume
            max_size_by_liquidity = avg_volume_5m * 0.05

            final_size = min(risk_based_size, max_size_by_liquidity)
            return float(final_size)
            
        except Exception as e:
            logger.error(f"[Governor Critical] Exception during position size calculation: {e}")
            return 0.0

    def trigger_circuit_breaker(self, reason: str) -> None:
        """Global kill switch: disables all new orders and alerts securely."""
        if self.is_halted:
            return  # Prevent redundant triggers

        self.is_halted = True
        error_msg = f"[GOVERNOR HALT TRIGGERED] {reason}"
        logger.critical(error_msg)

        try:
            # Immediate push notification via secure notifier channel
            send_alert(error_msg)
        except Exception as e:
            logger.error(f"[Governor Error] Failed to dispatch emergency notification alert: {e}")

    def check_health(self, connectivity_status: bool, current_daily_loss: float) -> None:
        """Monitors system health metrics every operational cycle."""
        try:
            self.daily_loss = float(current_daily_loss)
            
            if self.daily_loss >= self.max_daily_loss:
                self.trigger_circuit_breaker(f"Max daily loss limit reached (${self.daily_loss:,.2f} / ${self.max_daily_loss:,.2f})")

            if not connectivity_status:
                self.trigger_circuit_breaker("Broker connectivity lost or unstable.")
                
        except Exception as e:
            logger.error(f"[Governor Critical] Error during health check evaluation: {e}")

