# ~/QuantBot/config.py
import os
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

class Config:
    # Pulling from .env file
    ALPACA_API_KEY = os.getenv("ALPACA_KEY_APEX_001")
    ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_APEX_001")

    # Core Risk Parameters
    RISK_PER_TRADE = 0.05
    MAX_DAILY_DRAWDOWN = 0.10
    ATR_PERIOD = 14
