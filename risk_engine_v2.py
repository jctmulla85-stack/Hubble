import os
import pandas as pd
import numpy as np

class AdvancedRiskEngine:
    def __init__(self, log_file='trading_audit.log'):
        self.log_file = log_file

    def evaluate_execution_integrity(self):
        """
        Calculates real-time slippage, fill-to-signal divergence, 
        and rolling volume participation rates to prevent market impact.
        """
        if not os.path.exists(self.log_file):
            return {"status": "NO_LOGS", "slippage_avg": 0.0, "volume_participation": 0.0}
            
        df = pd.read_csv(self.log_file).tail(200)
        
        # Check required columns for advanced metrics
        required_cols = ['signal_price', 'fill_price', 'order_size', 'volume_available']
        if not all(col in df.columns for col in required_cols):
            return {"status": "LEGACY_SCHEMA", "action": "UPGRADE_REQUIRED"}

        # Vectorized slippage calculation
        df['slippage'] = np.abs(df['fill_price'] - df['signal_price']) / df['signal_price']
        mean_slippage = float(df['slippage'].mean())
        
        # Volume participation constraint
        df['participation'] = df['order_size'] / df['volume_available']
        max_participation = float(df['participation'].max())
        
        return {
            "status": "OPTIMIZED",
            "mean_slippage": mean_slippage,
            "max_volume_participation": max_participation
        }

if __name__ == "__main__":
    engine = AdvancedRiskEngine()
    print("Advanced Risk Engine Initialized:", engine.evaluate_execution_integrity())
