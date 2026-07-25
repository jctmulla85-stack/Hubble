import os
import json
import logging
from datetime import datetime
import pytz
from typing import Dict, Any, List

# Configure enterprise-grade secure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("QuantBot.Strategy")

class MomentumStrategy:
    """
    Enterprise-Grade Adaptive Momentum Strategy.
    Designed for high-throughput, secure, multi-asset manifest execution,
    adhering to modern quantitative trading and security architecture.
    """
    def __init__(self, event_bus: Any, manifest_path: str = 'trading_manifest.json'):
        self.bus = event_bus
        self.current_regime = "NEUTRAL"
        self.manifest_path = manifest_path

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

    def run_tick(self) -> None:
        """
        Main execution tick loop evaluated periodically.
        Bypasses strategy evaluation and broker calls when the market is closed.
        """
        if not self._is_market_open():
            # Market is closed; skip execution loops to prevent off-hours connection vetoes
            return

        # --- Your existing strategy execution and signal evaluation logic goes here ---
        logger.info("Market is open. Running strategy tick evaluation...")

