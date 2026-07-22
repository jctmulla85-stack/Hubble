import logging
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np

# Configure dedicated risk audit logging
logger = logging.getLogger("QuantBot.RiskEngine")

class RiskEngine:
    """
    Enterprise-Grade Risk Management & Volatility Sizing Engine.
    Ensures strict adherence to capital preservation and adaptive position sizing.
    """
    def __init__(self, default_risk_pct: float = 0.01) -> None:
        self.default_risk_pct = default_risk_pct
        logger.info("RiskEngine initialized with strict volatility sizing parameters.")

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> Optional[float]:
        """Calculates Average True Range (ATR) with defensive schema and boundary checks."""
        try:
            if df is None or not isinstance(df, pd.DataFrame):
                logger.error("[Risk Error] Invalid or null DataFrame provided for ATR calculation.")
                return None
            
            required_columns = {'high', 'low', 'close'}
            if not required_columns.issubset(df.columns):
                logger.error(f"[Risk Error] DataFrame missing required price columns. Expected {required_columns}")
                return None

            if len(df) < period:
                logger.warning(f"[Risk Warning] DataFrame length ({len(df)}) is less than ATR period ({period}).")
                return None

            high = df['high']
            low = df['low']
            close = df['close']

            tr1 = high - low
            tr2 = (high - close.shift(1)).abs()
            tr3 = (low - close.shift(1)).abs()

            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr_series = tr.rolling(window=period).mean()
            
            latest_atr = atr_series.iloc[-1]
            if pd.isna(latest_atr) or latest_atr <= 0:
                logger.warning("[Risk Warning] Calculated ATR is zero, NaN, or negative.")
                return None

            return float(latest_atr)

        except Exception as e:
            logger.error(f"[Risk Critical] Unhandled exception during ATR calculation: {e}")
            return None

    def get_dynamic_qty(self, account_equity: float, risk_pct: Optional[float], atr_value: Optional[float], price: float) -> float:
        """
        Calculates institutional position sizing: Risk % of equity per trade with a 2*ATR stop-loss buffer.
        """
        try:
            if account_equity <= 0 or price <= 0:
                logger.warning("[Risk Warning] Account equity or asset price is non-positive. Sizing aborted.")
                return 0.0

            if atr_value is None or atr_value <= 0:
                logger.warning("[Risk Warning] Invalid ATR value passed to sizing engine. Sizing aborted.")
                return 0.0

            active_risk_pct = risk_pct if risk_pct is not None else self.default_risk_pct
            risk_amount = account_equity * active_risk_pct
            stop_distance = atr_value * 2.0

            if stop_distance == 0:
                return 0.0

            # Quantitative position sizing formula: Risk capital divided by stop distance (volatility unit)
            raw_qty = risk_amount / stop_distance
            final_qty = round(raw_qty, 2)

            logger.info(f"[Risk Sizing] Equity: {account_equity}, ATR: {atr_value:.4f}, Price: {price}, Sized Qty: {final_qty}")
            return max(0.0, final_qty)

        except Exception as e:
            logger.error(f"[Risk Critical] Exception encountered in dynamic quantity calculation: {e}")
            return 0.0

