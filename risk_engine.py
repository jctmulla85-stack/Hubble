import sys
from state_guard import StateReconciliationGuard
from execution_guard import ExecutionHeartbeatGuard
from flow_guard import OrderFlowGuard
from portfolio_manager import PortfolioManager

class UnifiedRiskEngine:
    def __init__(self, max_drift=0.01, max_latency_ms=15.0, max_slippage=0.005, imbalance_threshold=0.75, max_total_exposure=500000.0):
        self.state_guard = StateReconciliationGuard(max_allowed_drift_pct=max_drift)
        self.execution_guard = ExecutionHeartbeatGuard(max_latency_ms=max_latency_ms, max_slippage_pct=max_slippage)
        self.flow_guard = OrderFlowGuard(imbalance_threshold=imbalance_threshold)
        self.portfolio_manager = PortfolioManager(max_total_exposure=max_total_exposure)

    def pre_flight_check(self, local_bal, broker_bal, local_pos, broker_pos, bid_vol, ask_vol, symbol=None, qty=0, price=0.0):
        """
        Executes full zero-dependency validation pipeline including 
        heartbeat, state drift, flow toxicity, and portfolio exposure limits.
        """
        # 1. Heartbeat check
        self.execution_guard.record_heartbeat()

        # 2. State reconciliation check
        self.state_guard.verify_state(local_bal, broker_bal, local_pos, broker_pos)

        # 3. Order flow imbalance check
        if not self.flow_guard.evaluate_imbalance(bid_vol, ask_vol):
            sys.stderr.write("[RISK_ENGINE] Toxic order flow detected. Signal rejected.\n")
            return False

        # 4. Portfolio exposure limit check (if trade parameters are provided)
        if symbol and qty != 0 and price > 0.0:
            if not self.portfolio_manager.validate_new_exposure(symbol, qty, price):
                sys.stderr.write("[RISK_ENGINE] Portfolio exposure limit exceeded. Signal rejected.\n")
                return False

        return True
