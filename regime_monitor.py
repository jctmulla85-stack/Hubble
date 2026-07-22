import os
import logging
from typing import Optional, Literal
import pandas as pd
import numpy as np

# Secure Imports from internal modules
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

# Define strict regime type boundaries
MarketRegime = Literal['TRENDING', 'RANGING', 'VOLATILE']

def get_market_regime(log_file: str = 'trading_audit.log') -> MarketRegime:
    """
    Analyzes recent trade audit telemetry to classify the current market state.
    Returns: 'TRENDING', 'RANGING', or 'VOLATILE'
    """
    logger.info(f"[Regime Monitor] Evaluating market regime from log source: {log_file}")

    try:
        # 1. Defensive File Existence Check
        if not os.path.exists(log_file):
            logger.warning(f"[Regime Warning] Log file not found at {log_file}. Defaulting to safe state: RANGING")
            return "RANGING"

        # 2. Robust Data Loading & Schema Validation
        try:
            df = pd.read_csv(log_file)
        except pd.errors.EmptyDataError:
            logger.warning(f"[Regime Warning] Log file {log_file} is empty. Defaulting to safe state: RANGING")
            return "RANGING"
        except Exception as e:
            logger.error(f"[Regime Error] Failed to parse log file CSV: {e}")
            return "RANGING"

        required_column = 'price'
        if required_column not in df.columns:
            logger.error(f"[Regime Error] Required column '{required_column}' missing from audit log schema.")
            return "RANGING"

        if len(df) < 5:
            logger.warning("[Regime Warning] Insufficient data points in log for reliable classification. Defaulting to RANGING.")
            return "RANGING"

        # Isolate recent activity tail
        recent_df = df.tail(100).copy()
        
        # Ensure price column is numeric and clean NaNs
        recent_df[required_column] = pd.to_numeric(recent_df[required_column], errors='coerce')
        price_series = recent_df[required_column].dropna()

        if len(price_series) < 5:
            logger.warning("[Regime Warning] Not enough valid numeric price points after cleaning.")
            return "RANGING"

        # 3. Calculate Key Quantitative Metrics
        volatility = float(price_series.pct_change().std())
        max_price = float(price_series.max())
        min_price = float(price_series.min())
        mean_price = float(price_series.mean())
        
        price_range = max_price - min_price

        if mean_price == 0:
            logger.error("[Regime Error] Mean price is zero; division by zero prevented.")
            return "RANGING"

        # 4. Adaptive Regime Logic Thresholds
        # High volatility threshold filter
        if volatility > 0.02:
            logger.info(f"[Regime Classification] High volatility detected ({volatility:.4f}). State: VOLATILE")
            return "VOLATILE"

        # Trend vs Range logic based on range relative to mean price
        if (price_range / mean_price) > 0.05:
            logger.info(f"[Regime Classification] Significant price range detected. State: TRENDING")
            return "TRENDING"
        else:
            logger.info(f"[Regime Classification] Stable price movement detected. State: RANGING")
            return "RANGING"

    except Exception as e:
        logger.error(f"[Regime Critical] Unhandled exception during market regime classification: {e}")
        return "RANGING"  # Default safe state fallback

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_PATH = os.path.join(BASE_DIR, 'trading_audit.log')
    
    regime = get_market_regime(LOG_PATH)
    print(f"[MONITOR] Current Market Regime: {regime}")

