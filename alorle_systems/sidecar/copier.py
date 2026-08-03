import struct
from typing import List, Dict
from sidecar.state_manager import StateJournal
from sidecar.engine import ConstraintMeshEngine

class AccountTarget:
    def __init__(self, account_id: int, multiplier: float = 1.0, max_dd_pct: float = 0.045):
        self.account_id = account_id
        self.multiplier = multiplier
        # Initialize an independent constraint mesh instance for each target account
        self.journal = StateJournal()
        self.engine = ConstraintMeshEngine(state_journal=self.journal, max_daily_drawdown_pct=max_dd_pct)

class MultiAccountCopier:
    def __init__(self, targets: List[AccountTarget]):
        self.targets = targets

    def distribute_signal(self, parent_action: int, parent_volume: float, price: float) -> Dict[int, bool]:
        execution_results = {}

        print(f"[Copier] Distributing parent signal (Action: {parent_action}, Vol: {parent_volume}) across {len(self.targets)} accounts...")

        for target in self.targets:
            # Calculate scaled volume for this specific account target
            child_volume = round(parent_volume * target.multiplier, 4)
            
            # Run the child order through its own isolated constraint mesh
            approved = target.engine.evaluate_signal(
                account_id=target.account_id,
                proposed_action=parent_action,
                volume=child_volume,
                price=price
            )

            execution_results[target.account_id] = approved
            
            if approved:
                print(f"[Copier] -> Account {target.account_id}: APPROVED [Scaled Vol: {child_volume}]")
            else:
                print(f"[Copier] -> Account {target.account_id}: BLOCKED by isolated constraint mesh.")

        return execution_results
