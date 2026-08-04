import os
import argparse
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import ClosePositionRequest

def liquidate_all_positions(account_id: str):
    api_key = os.getenv(f"ALPACA_KEY_{account_id}")
    api_secret = os.getenv(f"ALPACA_SECRET_{account_id}")
    
    if not api_key or not api_secret:
        print(f"[Error] Credentials not found for account: {account_id}")
        return

    client = TradingClient(api_key, api_secret, paper=True)
    
    print(f"[Liquidation] Closing all open positions and canceling open orders for {account_id}...")
    # Cancel all open orders first
    client.cancel_orders()
    
    # Close all open positions
    closed_positions = client.close_all_positions(cancel_orders=True)
    print(f"[Liquidation] Successfully closed positions for {account_id}: {closed_positions}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    args = parser.parse_args()
    liquidate_all_positions(args.id)
