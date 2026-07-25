import os
import sys
import logging
from dotenv import load_dotenv

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from governance.logger import get_master_logger, log_event
from config import Config
from governance.governor import Governor
from governance.gatekeeper import Gatekeeper
from execution.backend import LiveAlpacaBackend as LiveAlpacaBackend
from archive.test_connection import client as alpaca_client
import subprocess

def main():
    logger = get_master_logger()
    try:
        logger.info("[Main Startup] Initializing Governor safety parameters and circuit breakers...")
        config_instance = Config()
        
        governor_instance = Governor(
            initial_equity=100000.0,
            risk_per_trade=getattr(config_instance, 'RISK_PER_TRADE', 0.01),
            max_daily_loss_pct=getattr(config_instance, 'MAX_DAILY_DRAWDOWN', 0.05)
        )
        logger.info("[Main Startup] Governor safety parameters and circuit breakers initialized.")

        live_backend = LiveAlpacaBackend(alpaca_client)
        logger.info("[Main Startup] Live execution backend successfully linked.")

        gatekeeper_instance = Gatekeeper(governor_instance, live_backend)
        logger.info("[Main Startup] Gatekeeper dependency injection complete.")

        print("System initialized with production LiveAlpacaBackend.")
        print("Gatekeeper is active and monitoring markets.")

        # Launch the unified controller orchestrator as a system of systems
        controller_path = os.path.join(BASE_DIR, 'controller.py')
        if os.path.exists(controller_path):
            log_event("INFO", "[Main Startup] Launching controller orchestrator process...")
            subprocess.Popen(['python3', controller_path])
        else:
            log_event("ERROR", "[Main Error] controller.py not found for system orchestration.")

    except Exception as e:
        logger.critical(f"[Main Critical] Failed to initialize system components: {e}")
        print(f"Failed to initialize system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
