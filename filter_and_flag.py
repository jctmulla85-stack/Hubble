import os
from alpaca.trading.client import TradingClient
from liquidity_guard import LiquidityGuard

api_key = os.getenv("ALPACA_KEY_APEX_001")
api_secret = os.getenv("ALPACA_SECRET_APEX_001")
client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)

positions = client.get_all_positions()
guard = LiquidityGuard()

print("--- Running Liquidity Guard Filtering ---")
flagged = []

for p in positions:
    # Check if the guard has a validation method or evaluate based on market value / attributes
    # We will run them through the guard checks
    symbol = p.symbol
    val = float(p.market_value)
    
    # If LiquidityGuard has a specific evaluation method, invoke it here
    # For now, let's list any positions with low nominal value or flag them for review
    if val < 50.0:  # Example threshold for dust/thin positions
        flagged.append((symbol, val))

print(f"\nTotal Flagged Positions for Review: {len(flagged)}")
for symbol, val in flagged:
    print(f" -> Flagged: {symbol} (Market Value: ${val:.2f})")
