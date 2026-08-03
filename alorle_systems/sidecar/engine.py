import time
from datetime import datetime, timezone
from sidecar.state_manager import StateJournal

class ConstraintMeshEngine:
    def __init__(self, state_journal: StateJournal, max_daily_drawdown_pct: float = 0.045, max_daily_profit_pct: float = 0.10):
        self.journal = state_journal
        self.max_daily_drawdown_pct = max_daily_drawdown_pct
        self.max_daily_profit_pct = max_daily_profit_pct # Mitigates consistency rule penalties

    def _is_restricted_time(self) -> bool:
        """Blocks trading over weekends or major rollover periods."""
        now = datetime.now(timezone.utc)
        # Example: Restrict Friday close (after 20:00 UTC) through Sunday open
        if now.weekday() == 5: # Saturday
            return True
        if now.weekday() == 4 and now.hour >= 20: # Friday post-market
            return True
        if now.weekday() == 6 and now.hour < 21: # Sunday pre-market
            return True
        return False

    def evaluate_signal(self, account_id: int, proposed_action: int, volume: float, price: float, unrealized_pnl: float = 0.0) -> bool:
        """Evaluates proposed trade against trailing equity drawdown, consistency caps, and time windows."""
        
        # 1. Check Weekend / Rollover Blackout Restrictions
        if self._is_restricted_time():
            print(f"[Mesh] BLOCKED: Account {account_id} trade rejected due to weekend/rollover blackout rule.")
            return False

        state = self.journal.get_account_state(account_id)
        if not state:
            print(f"[Mesh] BLOCKED: Account {account_id} state not found in journal.")
            return False

        if state['locked']:
            print(f"[Mesh] BLOCKED: Account {account_id} is locked due to prior rule breach.")
            return False

        peak_equity = state['peak_equity']
        current_equity = state['current_equity'] + unrealized_pnl # Real-time floating equity tracking

        # 2. Check Floating Equity Drawdown (Trailing Drawdown Protection)
        drawdown = peak_equity - current_equity
        drawdown_pct = drawdown / peak_equity if peak_equity > 0 else 0.0

        if drawdown_pct >= self.max_daily_drawdown_pct:
            print(f"[Mesh] BREACH: Account {account_id} hit max drawdown threshold! [{drawdown_pct*100:.2f}%]")
            self.journal.update_account_state(account_id, current_equity=current_equity, locked=1)
            return False

        # 3. Check Consistency Rule / Daily Profit Cap
        profit_made = current_equity - peak_equity
        profit_pct = profit_made / peak_equity if peak_equity > 0 else 0.0
        if profit_pct >= self.max_daily_profit_pct:
            print(f"[Mesh] BLOCKED: Account {account_id} reached daily consistency profit cap [{profit_pct*100:.2f}%].")
            return False

        print(f"[Mesh] APPROVED: Account {account_id} passed all compliance checks. DD: {drawdown_pct*100:.2f}%")
        return True

