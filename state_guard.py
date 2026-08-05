import time
import sys

class StateReconciliationGuard:
    def __init__(self, max_allowed_drift_pct=0.01):
        self.max_drift = max_allowed_drift_pct
        self.last_sync_timestamp = time.time()

    def verify_state(self, local_balance, broker_balance, local_positions, broker_positions):
        """
        Validates state integrity between local execution logs and broker reality.
        Trips a hard safety lock if discrepancies exceed tolerances.
        """
        current_time = time.time()
        
        if broker_balance <= 0:
            raise ValueError("Critical: Invalid broker balance reported.")
            
        drift = abs(local_balance - broker_balance) / broker_balance
        if drift > self.max_drift:
            self.emergency_halt(f"Balance drift detected: Local {local_balance} vs Broker {broker_balance} (Drift: {drift:.4f})")

        if local_positions != broker_positions:
            self.emergency_halt(f"Position mismatch: Local {local_positions} vs Broker {broker_positions}")

        self.last_sync_timestamp = current_time
        return True

    def emergency_halt(self, reason):
        """Immediately halts execution logic and flags system lock down."""
        sys.stderr.write(f"[FATAL_STATE_ERROR] {reason} -> ENFORCING HARD SYSTEM LOCKDOWN.\n")
        sys.exit(1)
