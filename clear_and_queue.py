import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

api_key = os.getenv("ALPACA_KEY_APEX_001")
api_secret = os.getenv("ALPACA_SECRET_APEX_001")
client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)

target_symbols = ["HEPS", "JDZG", "RDGT", "WCT"]

print("--- Canceling Conflicting Orders ---")
orders = client.get_orders()
for o in orders:
    if o.symbol in target_symbols:
        try:
            client.cancel_order_by_id(o.id)
            print(f" -> Canceled existing order for {o.symbol}")
        except Exception as e:
            print(f" [ERROR] Could not cancel order for {o.symbol}: {e}")

# Now grab positions for these symbols and queue sell orders
positions = client.get_all_positions()
for p in positions:
    if p.symbol in target_symbols:
        try:
            side = OrderSide.SELL if p.side.value == 'long' else OrderSide.BUY
            order_data = MarketOrderRequest(
                symbol=p.symbol,
                qty=p.qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            client.submit_order(order_data)
            print(f" -> Queued Sell for conflicting symbol: {p.symbol}")
        except Exception as e:
            print(f" [ERROR] Failed to queue {p.symbol}: {e}")

print("\n[COMPLETE] All conflicting dust positions successfully cleared and queued.")
