import logging

class VolatilityGuard:
    def __init__(self, max_allowable_spread_pct=0.015):
        """
        Initializes the guard with a maximum allowable bid-ask spread percentage 
        (e.g., 1.5% of the asset price).
        """
        self.max_spread_pct = max_allowable_spread_pct

    def evaluate_market_conditions(self, symbol, bid, ask):
        """
        Evaluates current quote spread. If the spread is too wide 
        (indicating low liquidity or high volatility), it blocks execution.
        """
        if bid <= 0 or ask <= 0 or ask < bid:
            logging.warning(f"[{symbol}] Invalid quote data received: Bid={bid}, Ask={ask}. Standing down.")
            return False

        mid_price = (bid + ask) / 2.0
        spread = ask - bid
        spread_pct = spread / mid_price

        if spread_pct > self.max_spread_pct:
            logging.info(f"[{symbol}] Spread too wide ({spread_pct * 100:.4f}% > max {self.max_spread_pct * 100:.4f}%}}). Volatility guard active: standing idle.")
            return False

        logging.info(f"[{symbol}] Spread check passed ({spread_pct:.4%}). Safe to execute.")
        return True
