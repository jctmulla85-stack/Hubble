import os
from alpaca.trading.client import TradingClient

for env_var in os.environ:
    if env_var.startswith('ALPACA_KEY_'):
        account_id = env_var.replace('ALPACA_KEY_', '')
        key = os.getenv(f'ALPACA_KEY_{account_id}')
        secret = os.getenv(f'ALPACA_SECRET_{account_id}')
        if key and secret:
            client = TradingClient(key, secret, paper=True)
            positions = client.get_all_positions()
            total_unrealized_pl = sum(float(p.unrealized_pl) for p in positions)
            print(f"Account: {account_id}")
            print(f"Total Open Positions: {len(positions)}")
            print(f"Total Unrealized P&L: ${total_unrealized_pl:.2f}")
            for p in positions:
                print(f"  - {p.symbol}: Qty {p.qty}, P&L ${float(p.unrealized_pl):.2f}")
