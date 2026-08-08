from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def build_order_request(symbol: str, qty: float, side: OrderSide, order_type: str = "market", limit_price: float = None, **kwargs):
    is_fractional = isinstance(qty, float) and not qty.is_integer()
    time_in_force = TimeInForce.DAY if is_fractional else TimeInForce.GTC

    if order_type.lower() == "market":
        return MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=time_in_force)
    elif order_type.lower() == "limit":
        if limit_price is None:
            raise ValueError("Limit orders require a valid limit_price.")
        return LimitOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=time_in_force, limit_price=limit_price)
    else:
        raise ValueError(f"Unsupported order type: {order_type}")
