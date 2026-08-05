import os
from alpaca.trading.client import TradingClient

api_key = os.getenv("ALPACA_KEY_APEX_001")
api_secret = os.getenv("ALPACA_SECRET_APEX_001")

client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)

positions = client.get_all_positions()
account = client.get_account()

print("--- Portfolio Audit ---")
print(f"Total Equity: ${float(account.equity):,.2f}")
print(f"Cash Balance: ${float(account.cash):,.2f}")
print(f"Open Positions Count: {len(positions)}\n")

pos_dict = {p.symbol: float(p.market_value) for p in positions}
print("Positions:", pos_dict)
