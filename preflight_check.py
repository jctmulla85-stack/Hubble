import os
from alpaca.trading.client import TradingClient

for env_var in os.environ:
    if env_var.startswith('ALPACA_KEY_'):
        account_id = env_var.replace('ALPACA_KEY_', '')
        key = os.getenv(f'ALPACA_KEY_{account_id}')
        secret = os.getenv(f'ALPACA_SECRET_{account_id}')
        if key and secret:
            client = TradingClient(key, secret, paper=True)
            clock = client.get_clock()
            account = client.get_account()
            
            print(f"=== PRE-FLIGHT CHECK: {account_id} ===")
            print(f"API Connection:     SUCCESS")
            print(f"Market Next Open:   {clock.next_open}")
            print(f"Market Is Open:     {clock.is_open}")
            print(f"Account Status:     {account.status}")
            print(f"Buying Power:       ${float(account.buying_power):,.2f}")
            print("========================================")
