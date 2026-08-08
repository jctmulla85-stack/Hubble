import logging
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

class OrderExecutor:
    def __init__(self, trading_client, default_notional_usd=100.0):
        self.client = trading_client
        self.default_notional_usd = default_notional_usd

    def submit_buy_order(self, symbol, notional=None):
        target_notional = notional if notional else self.default_notional_usd
        try:
            asset = self.client.get_asset(symbol)
            if getattr(asset, 'fractionable', False):
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    notional=target_notional,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
            else:
                trade = self.client.get_latest_trade(symbol)
                current_price = float(trade.price)
                whole_shares = int(target_notional // current_price)
                if whole_shares > 0:
                    order_data = MarketOrderRequest(
                        symbol=symbol,
                        qty=whole_shares,
                        side=OrderSide.BUY,
                        time_in_force=TimeInForce.DAY
                    )
                else:
                    logging.warning(f"[ORDER SKIP] Notional ${target_notional} too low for 1 share of non-fractionable {symbol} at ${current_price}")
                    return None

            order = self.client.submit_order(order_data=order_data)
            logging.info(f"[ORDER SUBMITTED] {symbol} | Order ID: {order.id}")
            return order
        except Exception as e:
            logging.error(f"[ORDER ERROR] Failed to submit order for {symbol}: {e}")
            return None
