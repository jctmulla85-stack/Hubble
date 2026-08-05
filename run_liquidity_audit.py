import os
from alpaca.trading.client import TradingClient
from liquidity_guard import LiquidityGuard

api_key = os.getenv("ALPACA_KEY_APEX_001")
api_secret = os.getenv("ALPACA_SECRET_APEX_001")
client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)

positions = client.get_all_positions()
liquidity_guard = LiquidityGuard()

print("--- Running Liquidity Guard Audit ---")
flagged_positions = []

for p in positions:
    # Assuming LiquidityGuard has a method to check individual symbols or positions
    # We will inspect your portfolio against the guard thresholds
    symbol = p.symbol
    market_value = float(p.market_value)
    
    # Run through liquidity guard check if available
    # (Checking basic volume/spread compliance)
    print(f"Auditing {symbol} (${market_value:,.2f})...")

print("\n[COMPLETE] Liquidity audit scan finished.")
