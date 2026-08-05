import sys

class PortfolioManager:
    def __init__(self, max_total_exposure=500000.0):
        self.max_exposure = max_total_exposure
        self.positions = {}  # {symbol: {'qty': qty, 'cost_basis': price}}

    def update_position(self, symbol, qty, price):
        """Updates or initializes position state for any given asset."""
        if qty == 0:
            if symbol in self.positions:
                del self.positions[symbol]
        else:
            self.positions[symbol] = {'qty': qty, 'cost_basis': price}

    def get_total_exposure(self):
        """Calculates aggregate portfolio exposure across all active assets."""
        total = sum(abs(pos['qty'] * pos['cost_basis']) for pos in self.positions.values())
        return total

    def validate_new_exposure(self, symbol, additional_qty, price):
        """Ensures adding a position across any asset doesn't breach capital limits."""
        current_exposure = self.get_total_exposure()
        added_exposure = abs(additional_qty * price)
        
        if (current_exposure + added_exposure) > self.max_exposure:
            sys.stderr.write(f"[PORTFOLIO_MANAGER] Exposure limit breached for {symbol}. Order rejected.\n")
            return False
            
        return True
