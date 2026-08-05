import os
import pandas as pd
import alpaca_trade_api as tradeapi

def get_live_metrics(log_file='trading_audit.log'):
    try:
        # Fetch live account data from Alpaca API
        api = tradeapi.REST(
            key_id=os.environ["ALPACA_KEY_APEX_001"], 
            secret_key=os.environ["ALPACA_SECRET_APEX_001"], 
            base_url="https://paper-api.alpaca.markets"
        )
        acc = api.get_account()
        equity = float(acc.portfolio_value)
        initial_margin = float(acc.initial_margin)
        margin_ratio = (initial_margin / equity) if equity > 0 else 1.0

        # Calculate drawdown from local logs
        df = pd.read_csv(log_file).tail(200)
        curr = df['price'].iloc[-1]
        drawdown = (df['price'].max() - curr) / df['price'].max()

        return {
            "drawdown": drawdown,
            "margin_ratio": margin_ratio,
            "trade_count_hourly": len(df),
            "api_health": True
        }
    except Exception as e:
        # Safe-fail: If API or log fails, return Red status
        return {
            "drawdown": 1.0, 
            "margin_ratio": 999.0, 
            "trade_count_hourly": 999, 
            "api_health": False
        }
