from governance.kill_switch import DrawdownProtector
from memory.state_manager import StateManager
from memory.pnl_tracker import PnLTracker

def run_stress_test():
    print("--- STARTING STRESS TEST ---")

    # 1. Setup simulated environment
    sm = StateManager("test_state.json")
    pnl_tracker = PnLTracker(sm)
    protector = DrawdownProtector(max_daily_loss=50.0) # $50 limit

    # 2. Simulate a crash
    # Mocking a trade entry and subsequent price drop
    sm.state['entry_prices'] = {"SPY": 500.0}
    sm.state['positions'] = {"SPY": 1}

    current_price = 440.0 # Price drop causing $60 loss
    current_pnl = pnl_tracker.calculate_pnl("SPY", current_price)

    # 3. Test Reflexive Kill-Switch
    if not protector.is_safe(current_pnl):
        print(f"REFLEX TRIGGERED: PnL is {current_pnl}. SYSTEM HIBERNATING.")
    else:
        print("SYSTEM OPERATING NORMALLY.")

if __name__ == "__main__":
    run_stress_test()
