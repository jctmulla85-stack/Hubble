class PnLTracker:
    def __init__(self, state_manager):
        self.state = state_manager

    def calculate_pnl(self, symbol, current_price):
        position = self.state.state['positions'].get(symbol, 0)
        entry_price = self.state.state.get('entry_prices', {}).get(symbol, 0)

        # PnL = (Current Price - Entry Price) * Position
        pnl = (current_price - entry_price) * position
        return pnl
