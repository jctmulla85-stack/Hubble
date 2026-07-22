import pandas as pd

def get_live_metrics(log_file='trading_audit.log'):
    try:
        # Assumes log has 'price' and 'timestamp' columns
        df = pd.read_csv(log_file).tail(200)
        curr = df['price'].iloc[-1]
        drawdown = (df['price'].max() - curr) / df['price'].max()
        return {"drawdown": drawdown, "trade_count_hourly": len(df), "api_health": True}
    except Exception:
        # Safe-fail: If log is missing, return Red status
        return {"drawdown": 1.0, "trade_count_hourly": 999, "api_health": False}
