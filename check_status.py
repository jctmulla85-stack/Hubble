import os

# Read .env file directly if it exists in the current directory
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

api_key = os.getenv("APCA_API_KEY_ID") or os.getenv("ALPACA_API_KEY")
api_secret = os.getenv("APCA_API_SECRET_KEY") or os.getenv("ALPACA_SECRET_KEY")

client = TradingClient(api_key, api_secret, paper=True)

print("--- OPEN POSITIONS ---")
positions = client.get_all_positions()
if not positions:
    print("No open positions currently held.")
else:
    for p in positions:
        print(f"Symbol: {p.symbol} | Qty: {p.qty} | Side: {p.side} | Market Value: ${p.market_value}")

print("\n--- RECENT ORDERS ---")
request_params = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=10)
orders = client.get_orders(filter=request_params)
if not orders:
    print("No recent orders found.")
else:
    for o in orders:
        print(f"ID: {o.id} | Symbol: {o.symbol} | Side: {o.side} | Status: {o.status} | Type: {o.order_type}")
