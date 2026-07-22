import os
import sys
import time
import logging
import traceback

# --- Path Setup & Validation ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

RESEARCH_DIR = os.path.join(BASE_DIR, 'research')
if RESEARCH_DIR not in sys.path:
    sys.path.append(RESEARCH_DIR)

# Secure Imports from internal modules
from logger import get_master_logger
from governance.governor import Governor
from execution.reconciler import Reconciler
from momentum_strategy import MomentumStrategy

# --- Master Logger Setup ---
logger = get_master_logger()

def main_loop() -> None:
    """
    Core execution loop that coordinates the Governor, Reconciler, 
    and Momentum Strategy with defensive safeguards and telemetry monitoring.
    """
    logger.info("[Monitor & Execute] Initializing primary trading loop...")
    print("[MONITOR] Entering main_loop...")

    while True:
        try:
            # 1. Initialize Core Components securely
            logger.info("[Monitor & Execute] Instantiating Governor, Reconciler, and Strategy...")
            gov = Governor(initial_equity=50000.0)
            rec = Reconciler(governor=gov)
            strategy = MomentumStrategy(account_id="MULLA_85_ACC")

            # 2. Continuous Execution Cycle
            while True:
                broker_balance = strategy.get_broker_balance()
                
                if broker_balance is None:
                    logger.warning("[Monitor Warning] Failed to retrieve broker balance. Retrying next cycle.")
                    time.sleep(10)
                    continue

                # Verify state consistency via Reconciler
                if not rec.verify_state(strategy.internal_ledger, broker_balance):
                    error_msg = "[Monitor Critical] State verification failed between internal ledger and broker balance. Breaking loop for safety."
                    logger.error(error_msg)
                    print(error_msg)
                    break

                # Execute strategy tick
                strategy.run_tick(governor=gov)
                
                # Sleep interval between operational ticks
                time.sleep(60)

        except Exception as e:
            error_msg = f"[Monitor Critical Error] Unhandled exception in main loop: {e}"
            logger.error(error_msg)
            print(error_msg)
            traceback.print_exc()
            
            # Cooldown period before attempting recovery reboot
            logger.info("[Monitor Recovery] Pausing for 60 seconds before restarting main loop execution...")
            time.sleep(60)

if __name__ == "__main__":
    main_loop()

