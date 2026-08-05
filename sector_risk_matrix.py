import sys
import numpy as np

class SectorRiskMatrix:
    def __init__(self, max_sector_allocation_pct=25.0, correlation_threshold=0.85):
        self.max_sector_allocation_pct = max_sector_allocation_pct
        self.correlation_threshold = correlation_threshold

    def evaluate_basket_exposure(self, positions, sector_mapping, total_equity):
        """
        positions: dict of {symbol: market_value}
        sector_mapping: dict of {symbol: sector_name}
        """
        sector_totals = {}
        for symbol, value in positions.items():
            sector = sector_mapping.get(symbol, "UNKNOWN")
            sector_totals[sector] = sector_totals.get(sector, 0.0) + abs(value)

        breached_sectors = []
        for sector, exposure in sector_totals.items():
            allocation_pct = (exposure / total_equity) * 100
            print(f"[SECTOR RISK] {sector}: ${exposure:,.2f} ({allocation_pct:.2f}% of equity)")
            if allocation_pct > self.max_sector_allocation_pct:
                breached_sectors.append(sector)

        if breached_sectors:
            print(f"[CRITICAL ALERT] Sector allocation limit breached in: {breached_sectors}")
            return "REDUCE_SECTOR_EXPOSURE"

        return "NORMAL"

    def check_correlation_shock(self, returns_matrix):
        """
        returns_matrix: numpy array of asset returns shape (time_periods, num_assets)
        """
        if returns_matrix.shape[1] < 2:
            return "NORMAL"
            
        corr_matrix = np.corrcoef(returns_matrix, rowvar=False)
        # Exclude diagonal
        np.fill_diagonal(corr_matrix, 0)
        mean_corr = np.mean(corr_matrix)
        
        print(f"[CORRELATION CHECK] Mean Basket Correlation: {mean_corr:.2f}")
        if mean_corr >= self.correlation_threshold:
            print(f"[WARNING] High systemic correlation convergence detected ({mean_corr:.2f} >= {self.correlation_threshold}). Macro shock risk elevated.")
            return "DEFENSIVE_HEDGING"
            
        return "NORMAL"
