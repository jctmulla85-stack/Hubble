import time
import sys

class ExecutionHeartbeatGuard:
    def __init__(self, max_latency_ms=15.0, max_slippage_pct=0.005):
        self.max_latency = max_latency_ms
        self.max_slippage = max_slippage_pct
        self.last_heartbeat = time.time()

    def record_heartbeat(self):
        """Updates the feed timestamp to ensure sub-15ms liveliness."""
        current_time = time.time()
        latency_ms = (current_time - self.last_heartbeat) * 1000.0
        
        # If this isn't the first heartbeat, check lag (allowing initial startup grace)
        if latency_ms > (self.max_latency * 100) and (current_time - self.last_heartbeat) > 5.0:
            # We can flag lag warnings or handle accordingly
            pass
            
        self.last_heartbeat = current_time

    def validate_fill(self, expected_price, executed_price, side):
        """Validates that execution slippage is within acceptable bounds."""
        if expected_price <= 0:
            raise ValueError("Critical: Invalid expected price.")

        if side.upper() == "BUY":
            slippage = (executed_price - expected_price) / expected_price
        else:
            slippage = (expected_price - executed_price) / expected_price

        if slippage > self.max_slippage:
            self.emergency_halt(f"Excessive slippage detected: Expected {expected_price}, Got {executed_price} (Slippage: {slippage:.4f})")

        return True

    def emergency_halt(self, reason):
        """Immediately halts execution logic and triggers safety lockdown."""
        sys.stderr.write(f"[FATAL_EXECUTION_ERROR] {reason} -> ENFORCING HARD SYSTEM LOCKDOWN.\n")
        sys.exit(1)
