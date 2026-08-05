import sys

class MomentumStrategy:
    def __init__(self, threshold_imbalance=1.1):
        self.threshold_imbalance = threshold_imbalance
        sys.stdout.write("[STRATEGY] Initialized Zero-Dependency Momentum Strategy.\n")

    def generate_signal(self, symbol, quote):
        bid_vol = quote["bid_vol"]
        ask_vol = quote["ask_vol"]
        
        if ask_vol == 0:
            return "HOLD"
            
        ratio = bid_vol / ask_vol
        
        if ratio >= self.threshold_imbalance:
            sys.stdout.write(f"[STRATEGY] Bullish imbalance detected for {symbol} (Ratio: {ratio:.2f}). Signal: BUY\n")
            return "BUY"
        elif ratio <= (1.0 / self.threshold_imbalance):
            sys.stdout.write(f"[STRATEGY] Bearish imbalance detected for {symbol} (Ratio: {ratio:.2f}). Signal: SELL\n")
            return "SELL"
            
        return "HOLD"
