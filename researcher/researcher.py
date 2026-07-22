import pandas as pd
import os
import random

class Researcher:
    def fetch_latest_bars(self, symbol):
        # MOCK DATA: Generates random price movement for testing
        if os.getenv("BOT_MODE") == "MOCK":
            price = 100 + random.uniform(-2, 2)
            return pd.DataFrame({'high': [price], 'low': [price - 1]})

        # Real API call (placeholder)
        # return api.get_bars(symbol, ...)
        return pd.DataFrame()

    def analyze_signal(self, df):
        # MOCK LOGIC: Returns buy/sell based on random chance for testing
        if os.getenv("BOT_MODE") == "MOCK":
            return random.choice(["BUY", "SELL", "HOLD"])
        return "HOLD"
