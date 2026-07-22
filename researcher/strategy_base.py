class StrategyBase:
    def __init__(self, account_id):
        self.account_id = account_id

    def generate_signal(self, market_data):
        """
        Must return a signal dictionary or None.
        Format: {"symbol": "AAPL", "side": "buy", "qty": 10, "type": "market"}
        """
        raise NotImplementedError("Strategy must implement generate_signal")
