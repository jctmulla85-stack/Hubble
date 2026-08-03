from sidecar.state_manager import StateJournal
from sidecar.engine import ConstraintMeshEngine

journal = StateJournal()
engine = ConstraintMeshEngine(state_journal=journal, max_daily_drawdown_pct=0.045)

account_id = 998877

# Set initial healthy state: $50,000 peak, $50,000 current
journal.update_account_state(account_id, current_equity=50000.0, locked=0)
print("[Test] Evaluating normal trading signal...")
engine.evaluate_signal(account_id, proposed_action=1, volume=1.0, price=100.0)

# Simulate a heavy drawdown breaching the 4.5% limit (dropping equity to $47,000 -> 6% drawdown)
print("\n[Test] Simulating drawdown drop to $47,000...")
journal.update_account_state(account_id, current_equity=47000.0, locked=0)

# Evaluate next signal—should trigger lock
print("[Test] Evaluating signal during drawdown breach...")
engine.evaluate_signal(account_id, proposed_action=1, volume=1.0, price=100.0)

# Verify subsequent signals are blocked by the lock
print("[Test] Evaluating signal after account lock...")
engine.evaluate_signal(account_id, proposed_action=1, volume=1.0, price=100.0)
