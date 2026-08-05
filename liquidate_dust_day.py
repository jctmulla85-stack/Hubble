import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

api_key = os.getenv("ALPACA_KEY_APEX_001")
api_secret = os.getenv("ALPACA_SECRET_APEX_001")
client = TradingClient(api_key=api_key, secret_key=api_secret, paper=True)

positions = client.get_all_positions()

print("--- Queuing Dust Liquidations for Market Open ---")
liquidated_count = 0

for p in positions:
    val = float(p.market_value)
    if val < 50.0:
        try:
            side = OrderSide.SELL if p.side.value == 'long' else OrderSide.BUY
            order_data = MarketOrderRequest(
                symbol=p.symbol,
                qty=p.qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            client.submit_order(order_data)
            print(f" -> Queued Sell: {p.symbol} (Value: ${val:.2f})")
            liquidated_count += 1
        except Exception as e:
            print(f" [ERROR] Failed to queue {p.symbol}: {e}")

print(f"\n[COMPLETE] Successfully queued {liquidated_count} orders for market open.")
