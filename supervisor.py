import os
import sys
import logging
import subprocess
from typing import Dict, Any, Tuple

# Secure Imports from internal modules
from circuit_breaker import GovernanceAgent
from metrics_monitor import get_live_metrics
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

# --- Safety & Governance Thresholds ---
SAFETY: Dict[str, Any] = {
    "max_drawdown": 0.05,
    "max_trades_per_hour": 50
}

def run_governed_cycle() -> None:
    """
    Executes a secure governance check using the circuit breaker pattern.
    Blocks execution if drawdown or trade velocity thresholds are breached.
    """
    logger.info("[Supervisor] Initiating pre-flight governance safety evaluation.")
    
    try:
        metrics = get_live_metrics()
        if not isinstance(metrics, dict):
            logger.error("[Supervisor Error] Invalid metrics payload received from monitor. Halting execution.")
            return

        agent = GovernanceAgent(SAFETY)
        status, reason = agent.check_status(metrics)

        if status == "RED":
            logger.critical(f"[Supervisor Security] Trade execution blocked by Circuit Breaker: {reason}")
            return # Hard stop: Prevent worker initialization

        if status == "GREEN":
            logger.info("[Supervisor Security] Governance checks passed. Launching protected worker core...")
            # Execute worker process using safe subprocess arguments
            subprocess.run([sys.executable, "workers.py"], check=True)
        else:
            logger.warning(f"[Supervisor Warning] Unrecognized governance status returned: {status}")

    except subprocess.CalledProcessError as cpe:
        logger.error(f"[Supervisor Error] Protected worker subprocess terminated with non-zero exit code: {cpe}")
    except Exception as e:
        logger.error(f"[Supervisor Critical] Unhandled exception during governed execution cycle: {e}")

if __name__ == "__main__":
    run_governed_cycle()

