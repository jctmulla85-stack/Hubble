import circuit_breaker

def run_stress_test():
    # Simulate a market crash: High drawdown, massive trade frequency (Logic Drift)
    crash_metrics = {
        "drawdown": 0.15,          # 15% drop (Limit is 5%)
        "trade_count_hourly": 200, # 200 trades/hr (Limit is 50)
        "api_health": True
    }

    safety_template = {"max_drawdown": 0.05, "max_trades_per_hour": 50}
    agent = circuit_breaker.GovernanceAgent(safety_template)

    status, reason = agent.check_status(crash_metrics)

    if status == "RED":
        print(f"[SUCCESS] Circuit Breaker tripped during Stress Test! Reason: {reason}")
    else:
        print("[FAILURE] Circuit Breaker did not trip.")

if __name__ == "__main__":
    run_stress_test()
