# Import from the governance package
from governance.governor import Governor

def test_governor_scenarios():
    gov = Governor(initial_equity=50000, risk_per_trade=0.01)

    print("--- Running Phase 1: Stress Test ---")

    # 1. Test Liquidity Filter
    size = gov.calculate_position_size(100, 95, avg_volume_5m=10)
    assert size <= 0.5, f"Liquidity filter failed! Size was {size}"
    print("✓ Liquidity Filter: Passed")

    # 2. Test Drawdown Velocity
    gov.check_health(connectivity_status=True, current_daily_loss=3000)
    assert gov.is_halted == True, "Drawdown breaker failed to halt!"
    print("✓ Drawdown Breaker: Passed")

    # 3. Test Connectivity Breaker
    # Create fresh governor for clean state
    gov2 = Governor(initial_equity=50000)
    gov2.check_health(connectivity_status=False, current_daily_loss=0)
    assert gov2.is_halted == True, "Connectivity breaker failed to halt!"
    print("✓ Connectivity Breaker: Passed")

    print("--- Phase 1: All Stress Tests Passed ---")

if __name__ == "__main__":
    test_governor_scenarios()
