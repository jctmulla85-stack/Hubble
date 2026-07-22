import json
import pandas as pd
import numpy as np
import os
from datetime import datetime

def calculate_score(params, df):
    """Calculates performance with a penalty for complexity."""
    # 1. Simple Backtest (Mock logic based on params)
    returns = df['equity'].pct_change() * params.get('leverage', 1)
    sharpe = returns.mean() / returns.std() if returns.std() != 0 else 0

    # 2. Complexity Penalty (Occam's Razor: Keep it simple)
    # Penalize short windows (prone to noise) and high leverage
    penalty = (1.0 / params['window']) + (params['leverage'] * 0.1)

    return sharpe - penalty

def perform_stress_test(params, df):
    """Ensures the strategy doesn't violate your capital preservation rules."""
    # Simulate worst-case drawdown
    cumulative = (1 + (df['equity'].pct_change() * params.get('leverage', 1))).cumprod()
    peak = cumulative.expanding(min_periods=1).max()
    dd = (cumulative - peak) / peak

    # Hard Limit: 2% drawdown max in test data
    if dd.min() < -0.02:
        return False
    return True

def run_optimizer():
    # Load the audit data (your 'Feature Store')
    if not os.path.exists('audit_trail.jsonl'):
        return

    df = pd.read_json('audit_trail.jsonl', lines=True)

    # Walk-Forward Approach: Only optimize on the most recent 30-day window
    recent_df = df.tail(1000)

    # Candidate Space (Your R&D Hypotheses)
    candidates = [
        {'window': 20, 'threshold': 0.02, 'leverage': 1.0},
        {'window': 50, 'threshold': 0.05, 'leverage': 1.0},
        {'window': 100, 'threshold': 0.03, 'leverage': 1.0}
    ]

    best_params = None
    best_score = -np.inf

    for params in candidates:
        if perform_stress_test(params, recent_df):
            score = calculate_score(params, recent_df)
            if score > best_score:
                best_score = score
                best_params = params

    # Atomic Update: Only save if we found a valid, robust strategy
    if best_params:
        with open("memory/strategy_params.json", "w") as f:
            json.dump(best_params, f)
        print(f"[{datetime.now()}] Optimizer: New robust parameters deployed.")
    else:
        print("Optimizer: No safe parameters found. Maintaining current strategy.")

if __name__ == "__main__":
    run_optimizer()
