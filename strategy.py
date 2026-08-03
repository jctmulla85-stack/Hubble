import os
import sys
import json
import logging
from datetime import datetime
import pytz
from typing import Dict, Any, List

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from governance.enterprise_governor import EnterpriseGovernor

# Configure enterprise-grade secure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("QuantBot.Strategy")

class MomentumStrategy:
    """
    Enterprise-Grade Adaptive Momentum Strategy.
    Designed for high-throughput, secure, multi-asset manifest execution,
    adhering to modern quantitative trading and security architecture.
    Integrated with EnterpriseGovernor for global risk and exposure limits.
    """
    def __init__(self, event_bus: Any, manifest_path: str = 'trading_manifest.json'):
        self.bus = event_bus
        self.current_regime = "NEUTRAL"
        self.manifest_path = os.path.join(BASE_DIR, manifest_path)
        self.governor = EnterpriseGovernor()
        logger.info("[MomentumStrategy Initialized] EnterpriseGovernor attached successfully.")

    def _is_market_open(self) -> bool:
        """
        Validates if US equity markets are currently open (9:30 AM - 4:00 PM ET, Mon-Fri).
        """
        ny_tz = pytz.timezone("America/New_York")
        now_ny = datetime.now(ny_tz)

        # Weekend check (Saturday = 5, Sunday = 6)
        if now_ny.weekday() >= 5:
            return False

        market_open = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)

        return market_open <= now_ny <= market_close

    def _load_manifest(self) -> Dict[str, Any]:
        """Loads the trading manifest safely."""
        try:
            if not os.path.exists(self.manifest_path):
                logger.warning(f"[MomentumStrategy] Manifest not found at {self.manifest_path}. Using empty config.")
                return {}
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[MomentumStrategy Error] Failed to load trading manifest: {e}")
            return {}

    def run_tick(self) -> None:
        """
        Main execution tick loop evaluated periodically.
        Bypasses strategy evaluation and broker calls when the market is closed.
        Enforces GovernorGuard safety rules prior to signal generation.
        """
        if not self._is_market_open():
            # Market is closed; skip execution loops to prevent off-hours connection vetoes
            return

        logger.info("Market is open. Running strategy tick evaluation...")
        
        manifest = self._load_manifest()
        assets = manifest.get("assets", [])
        
        for asset in assets:
            symbol = asset.get("symbol")
            target_qty = asset.get("qty", 0.0)
            side = asset.get("side", "buy")
            
            if not symbol or target_qty <= 0:
                continue

            # Enforce enterprise risk governance check via GovernorGuard
            allowed, reason = self.governor.validate_order(symbol, target_qty, side)
            if not allowed:
                logger.warning(f"[GovernorBlock] Skipped order for {symbol}: {reason}")
                continue

            logger.info(f"[SignalApproved] Asset {symbol} passed GovernorGuard validation. Proceeding to execution dispatch.")
            # --- Broker execution dispatch hook goes here ---
