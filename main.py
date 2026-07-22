# ~/QuantBot/main.py
import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from governance.logger import get_master_logger
from config import Config
from governance.governor import Governor
from governance.gatekeeper import Gatekeeper
from execution.backend import LiveAlpacaBackend as LiveAlpacaBackend
from archive.test_connection import client as alpaca_client

# --- Master Logger Setup ---
logger = get_master_logger()

def main() -> None:
    """
    Enterprise Main Entry Point: Initializes configuration, governor, live backend, 
    and gatekeeper dependencies with robust error handling and telemetry tracking.
    """
    try:
        # 1. Load environment variables
        load_dotenv()
        logger.info("[Main Startup] Environment variables loaded successfully.")
        print("Initializing system components...")

        # 2. Instantiate the config object to access your settings
        config_instance = Config()
        logger.info("[Main Startup] Configuration instance successfully created.")

        # 3. Initialize Governor with explicit numerical arguments
        governor_instance = Governor(
            initial_equity=100000.0,
            risk_per_trade=getattr(config_instance, 'RISK_PER_TRADE', 0.01),
            max_daily_loss_pct=getattr(config_instance, 'MAX_DAILY_DRAWDOWN', 0.05)
        )
        logger.info("[Main Startup] Governor safety parameters and circuit breakers initialized.")

        # 4. Initialize the Live Backend
        live_backend = LiveAlpacaBackend(alpaca_client)
        logger.info("[Main Startup] Live execution backend successfully linked.")

        # 5. Inject dependencies into the Gatekeeper
        gatekeeper_instance = Gatekeeper(governor_instance, live_backend)
        logger.info("[Main Startup] Gatekeeper dependency injection complete.")

        print("System initialized with production LiveAlpacaBackend.")
        print("Gatekeeper is active and monitoring markets.")

    except Exception as e:
        logger.critical(f"[Main Critical] Failed to initialize system components: {e}")
        print(f"Failed to initialize system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

