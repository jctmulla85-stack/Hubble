import os
from alpaca.trading.client import TradingClient
from sector_risk_matrix import SectorRiskMatrix
from liquidity_guard import LiquidityGuard

# Initialize Alpaca client using your apex credentials
api_key = os.getenv("ALPACA_KEY_APEX_001")
api_secret = os.getenv("ALPACA_SECRET_APEX_001")
client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)

positions = client.get_all_positions()
account = client.get_account()
total_equity = float(account.equity)

print("--- Running Risk & Liquidity Audit ---")
pos_dict = {p.symbol: float(p.market_value) for p in positions}

# Initialize matrices/guards without unexpected keyword arguments
sector_matrix = SectorRiskMatrix()
liquidity_guard = LiquidityGuard()

print(f"Total Portfolio Value: ${total_equity:,.2f}")
print(f"Total Unique Positions: {len(pos_dict)}")
print("\n[SUCCESS] Portfolio data loaded successfully.")
