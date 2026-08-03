from sidecar.copier import MultiAccountCopier, AccountTarget
from sidecar.state_manager import StateJournal

# 1. Setup mock states for multiple prop accounts in our mmap journal
journal = StateJournal()
acc_alpha = 111111
acc_beta = 222222

journal.update_account_state(acc_alpha, current_equity=100000.0, locked=0)
journal.update_account_state(acc_beta, current_equity=48000.0, locked=0) # Below threshold simulation if needed

# 2. Define targets with different sizing multipliers and limits
targets = [
    AccountTarget(account_id=acc_alpha, multiplier=1.0, max_dd_pct=0.045),
    AccountTarget(account_id=acc_beta, multiplier=0.5, max_dd_pct=0.045)
]

copier = MultiAccountCopier(targets=targets)

# 3. Simulate parent order signal execution
print("[Test] Executing multi-account distribution...")
results = copier.distribute_signal(parent_action=1, parent_volume=2.0, price=65000.0)
print("[Test] Execution Results Summary:", results)
