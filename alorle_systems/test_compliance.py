from sidecar.engine import ConstraintMeshEngine
from sidecar.state_manager import StateJournal

journal = StateJournal()
acc_id = 555444

# Initialize account baseline state
journal.update_account_state(acc_id, current_equity=100000.0, locked=0)

engine = ConstraintMeshEngine(state_journal=journal, max_daily_drawdown_pct=0.045)

print("[Test] Running compliance constraint evaluation...")
# Test normal execution with floating unrealized equity
approved = engine.evaluate_signal(
    account_id=acc_id,
    proposed_action=1,
    volume=1.0,
    price=65000.0,
    unrealized_pnl=-500.0
)
print("[Test] Result:", approved)
