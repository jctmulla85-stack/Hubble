import os
import json
import time
import logging
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import schedule

# Secure Imports from internal modules
from governance.logger import log_event

# --- Master Logger Setup ---
# logger removed

# Configuration Constants
WATCHDOG_INTERVAL = 30
HEARTBEAT_TIMEOUT = 60
LOG_FILE = 'audit_trail.jsonl'

def run_optimizer() -> None:
    """Triggers the R&D Brain to evolve strategy parameters securely."""
    log_event("INFO", "[Controller] Launching R&D Optimization cycle...")
    try:
        optimizer_path = os.path.join('research', 'optimizer.py')
        if not os.path.exists(optimizer_path):
            log_event("ERROR", f"[Controller Error] Optimizer script missing at {optimizer_path}")
            return
            
        result = subprocess.run(['python3', optimizer_path], capture_output=True, text=True, check=True)
        log_event("INFO", f"[Controller] Optimizer completed successfully: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        log_event("ERROR", f"[Controller Error] Optimizer process failed: {e.stderr.strip()}")
    except Exception as e:
        log_event("ERROR", f"[Controller Critical] Unexpected error running optimizer: {e}")

def get_last_heartbeat(account_id: str) -> Optional[datetime]:
    """Verifies worker health by checking the audit trail securely with timezone awareness."""
    if not os.path.exists(LOG_FILE):
        return None

    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                data = entry.get("data", {})
                if data.get("account") == account_id and entry.get("type") == "SYSTEM_HEARTBEAT":
                    timestamp_str = entry.get("timestamp")
                    if timestamp_str:
                        dt = datetime.fromisoformat(timestamp_str)
                        # Ensure timezone awareness (UTC default if naive)
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return dt
            except (json.JSONDecodeError, ValueError):
                continue
    except Exception as e:
        log_event("ERROR", f"[Controller Error] Failed to read heartbeat log: {e}")

    return None

def run_orchestrator(accounts: List[str]) -> None:
    """Manages worker lifecycles, scheduled tasks, and watchdog checks."""
    processes: Dict[str, Optional[subprocess.Popen]] = {acc: None for acc in accounts}
    log_event("INFO", f"[Controller] Orchestrator initializing for accounts: {accounts}")

    # Schedule: Weekly R&D cycle (Sunday at 23:00)
    schedule.every().sunday.at("23:00").do(run_optimizer)

    # Initial Boot of Worker Processes
    for acc in accounts:
        worker_script = os.path.join('execution', 'worker.py')
        if not os.path.exists(worker_script):
            log_event("ERROR", f"[Controller Critical] Worker script not found at {worker_script}")
            continue
            
        log_event("INFO", f"[Controller] Booting worker process for account: {acc}")
        wlog = open(f'logs/worker_{acc}.log', 'a')
        processes[acc] = subprocess.Popen(['python3', '-u', worker_script, '--id', acc], stdout=wlog, stderr=wlog)

    # Continuous Feedback & Watchdog Loop
    try:
        while True:
            # Run scheduled background tasks (R&D)
            schedule.run_pending()

            # Watchdog: Ensure workers are alive and emitting heartbeats
            current_time = datetime.now(timezone.utc)
            for acc in accounts:
                last_hb = get_last_heartbeat(acc)
                proc = processes.get(acc)

                is_unresponsive = False
                if not last_hb:
                    log_event("WARNING", f"[Watchdog Warning] No heartbeat recorded yet for worker {acc}.")
                else:
                    delta_seconds = (current_time - last_hb).total_seconds()
                    if delta_seconds > HEARTBEAT_TIMEOUT:
                        log_event("WARNING", f"[Watchdog Alert] Worker {acc} missed heartbeat threshold ({delta_seconds:.1f}s elapsed).")
                        is_unresponsive = True

                # Check if process crashed or is unresponsive
                proc_dead = proc is None or proc.poll() is not None

                if proc_dead or is_unresponsive:
                    log_event("WARNING", f"[Watchdog Recovery] Restarting unresponsive/dead worker for account {acc}...")
                    
                    if proc and proc.poll() is None:
                        try:
                            proc.terminate()
                            proc.wait(timeout=5)
                        except Exception:
                            proc.kill()

                    worker_script = os.path.join('execution', 'worker.py')
                    wlog = open(f'logs/worker_{acc}.log', 'a')
                    processes[acc] = subprocess.Popen(['python3', '-u', worker_script, '--id', acc], stdout=wlog, stderr=wlog)
                    log_event("INFO", f"[Watchdog Recovery] Worker {acc} successfully restarted.")

            time.sleep(WATCHDOG_INTERVAL)

    except KeyboardInterrupt:
        log_event("INFO", "[Controller] Shutdown signal received. Terminating worker processes gracefully...")
        for acc, proc in processes.items():
            if proc and proc.poll() is None:
                proc.terminate()
        log_event("INFO", "[Controller] Orchestrator shutdown complete.")

if __name__ == "__main__":
    active_accounts = ["APEX_001"]
    run_orchestrator(active_accounts)

