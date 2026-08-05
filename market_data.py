import sys
import time

class MarketDataFeed:
    def __init__(self, symbols):
        self.symbols = symbols
        sys.stdout.write(f"[MARKET_DATA] Initialized feed for symbols: {', '.join(self.symbols)}\n")

    def get_latest_quote(self, symbol):
        """
        Simulates retrieving live bid/ask volumes and prices 
        with zero-overhead data structures.
        """
        if symbol not in self.symbols:
            raise ValueError(f"Symbol {symbol} not tracked in market data feed.")
            
        # Simulated live tick data (bid_vol, ask_vol, current_price)
        return {
            "symbol": symbol,
            "bid_vol": 1000,
            "ask_vol": 1150,
            "price": 150.0,
            "timestamp": time.time()
        }
