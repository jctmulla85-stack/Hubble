import sys

class LiquidityGuard:
    def __init__(self, max_spread_pct=0.01, min_volume=1000, max_slippage_pct=0.005):
        self.max_spread_pct = max_spread_pct
        self.min_volume = min_volume
        self.max_slippage_pct = max_slippage_pct

    def validate_order_execution(self, symbol, bid, ask, volume, expected_price):
        """
        Validates whether an asset meets strict microstructural liquidity requirements 
        prior to order routing.
        """
        if ask <= 0 or bid <= 0:
            print(f"[LIQUIDITY REJECT] {symbol}: Invalid quotes (Bid: {bid}, Ask: {ask})")
            return False

        spread_pct = (ask - bid) / ask
        print(f"[LIQUIDITY CHECK] {symbol} | Spread: {spread_pct:.4%}% | Volume: {volume:,}")

        if spread_pct > self.max_spread_pct:
            print(f"[REJECT] {symbol} spread ({spread_pct:.4%}) exceeds max threshold ({self.max_spread_pct:.4%})")
            return False

        if volume < self.min_volume:
            print(f"[REJECT] {symbol} volume ({volume:,}) below minimum threshold ({self.min_volume:,})")
            return False

        # Check potential slippage on expected execution price
        mid_price = (bid + ask) / 2.0
        slippage_pct = abs(expected_price - mid_price) / mid_price
        if slippage_pct > self.max_slippage_pct:
            print(f"[REJECT] {symbol} expected slippage ({slippage_pct:.4%}) exceeds limit ({self.max_slippage_pct:.4%})")
            return False

        return True
