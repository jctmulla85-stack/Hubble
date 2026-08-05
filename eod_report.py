import os
from alpaca.trading.client import TradingClient

for env_var in os.environ:
    if env_var.startswith('ALPACA_KEY_'):
        account_id = env_var.replace('ALPACA_KEY_', '')
        key = os.getenv(f'ALPACA_KEY_{account_id}')
        secret = os.getenv(f'ALPACA_SECRET_{account_id}')
        if key and secret:
            client = TradingClient(key, secret, paper=True)
            account = client.get_account()
            positions = client.get_all_positions()
            
            total_unrealized = sum(float(p.unrealized_pl) for p in positions)
            print(f"=== EOD REPORT FOR: {account_id} ===")
            print(f"Starting Baseline Equity: $100,000.00")
            print(f"Ending Equity:          ${float(account.equity):.2f}")
            print(f"Ending Cash:            ${float(account.cash):.2f}")
            print(f"Total Open Positions:   {len(positions)}")
            print(f"Total Unrealized P&L:   ${total_unrealized:.2f}")
            print(f"Day's Net Change ($):   ${float(account.equity) - 100000.00:.2f}")
            print("==================================")
