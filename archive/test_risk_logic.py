import numpy as np
import pandas as pd
from risk_engine import calculate_atr, get_dynamic_qty

# 1. Create Synthetic Data
np.random.seed(42)
days = 30
# Calm volatility for first 20 days, high for last 10
volatility = [0.1] * 20 + [0.5] * 10
prices = 100 + np.cumsum(np.random.normal(0, volatility, days))
data = pd.DataFrame({'high': prices + 0.5, 'low': prices - 0.5, 'close': prices})

# 2. Run the Engine
account_equity = 100000
risk_per_trade = 0.01

print(f"{'Day':<5} | {'Price':<8} | {'ATR':<8} | {'Suggested Qty'}")
print("-" * 40)

for i in range(14, days):
    window = data.iloc[i-14:i]
    atr = calculate_atr(window['high'], window['low'], window['close'])
    qty = get_dynamic_qty(account_equity, risk_per_trade, atr, window['close'].iloc[-1])
    print(f"{i:<5} | {data['close'].iloc[i]:<8.2f} | {atr:<8.2f} | {qty}")
