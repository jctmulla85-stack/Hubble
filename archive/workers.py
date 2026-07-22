import os
import json
import time
import logging
import sys
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# Secure Imports from internal modules
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

# Load environment variables securely
load_dotenv()

MANIFEST_PATH = 'trading_system.jsonl'

# Secure Credential Ingestion
api_key = os.getenv('ALPACA_KEY_APEX_001')
secret_key = os.getenv('ALPACA_SECRET_APEX_001')

if not api_key or not secret_key:
    logger.error("[Worker Critical] Alpaca API credentials missing from environment.")
    sys.exit(1)

# Initialize official Alpaca Trading Client (Paper trading mode active)
try:
    trade_client = TradingClient(api_key, secret_key, paper=True)
    logger.info("Enterprise TradingClient initialized securely.")
except Exception as e:
    logger.error(f"[Worker Critical] Failed to initialize TradingClient: {e}")
    sys.exit(1)

def log_to_risk_audit(message: str) -> None:
    """Appends trade and risk events to the audit audit trail securely."""
    try:
        audit_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "type": "RISK_AUDIT_EVENT",
            "data": {"message": message}
        }
        with open('audit_trail.jsonl', 'a') as f:
            f.write(json.dumps(audit_entry) + '\n')
    except Exception as e:
        logger.error(f"[Worker Error] Failed to write to risk audit trail: {e}")

def load_manifest() -> Dict[str, Any]:
    """Robustly load the asset manifest with exponential backoff and lock recovery."""
    if not os.path.exists(MANIFEST_PATH):
        logger.warning(f"[Worker] Manifest path not found: {MANIFEST_PATH}")
        return {}

    for attempt in range(5):
        try:
            with open(MANIFEST_PATH, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except (json.JSONDecodeError, PermissionError) as jde:
            logger.warning(f"[Worker] Read collision/lock on manifest (attempt {attempt+1}/5): {jde}")
            time.sleep(1.0 * (attempt + 1))
        except Exception as e:
            logger.error(f"[Worker Error] Unexpected manifest read exception: {e}")
            break

    return {}

def execute_beast_logic(assets: List[Dict[str, Any]]) -> None:
    """Core Execution Logic: High-throughput Profit-Taking & Stop-Loss risk filters."""
    logger.info(f"[Worker Execution] Scanning active universe of {len(assets)} assets.")

    try:
        raw_positions = trade_client.get_all_positions()
        positions = {p.symbol: p for p in raw_positions}
    except Exception as e:
        logger.error(f"[Worker Error] Failed to fetch live positions from broker: {e}")
        return

    for asset in assets:
        symbol = asset.get('symbol')
        if not symbol:
            continue

        if symbol in positions:
            pos = positions[symbol]
            try:
                gain = float(pos.unrealized_plpc)
            except (ValueError, TypeError) as conversion_err:
                logger.error(f"[Worker Error] Numeric parsing fault on position {symbol}: {conversion_err}")
                continue

            # 1. Profit-Taking: 5% gain threshold, secure 50% partial liquidity extraction
            if gain >= 0.05:
                try:
                    sell_qty = float(pos.qty) * 0.5
                    if sell_qty > 0:
                        trade_client.submit_order(
                            symbol_or_asset_id=symbol,
                            qty=sell_qty,
                            side='sell',
                            type='market',
                            time_in_force='gtc'
                        )
                        audit_msg = f"LIVE_TRADE: Secured 50% profit on {symbol} (Gain: {gain*100:.2f}%)"
                        log_to_risk_audit(audit_msg)
                        logger.info(audit_msg)
                except Exception as order_err:
                    logger.error(f"[Worker Order Error] Failed profit-taking execution on {symbol}: {order_err}")

            # 2. Stop-Loss: 5% loss threshold, full defensive liquidation (100%)
            elif gain <= -0.05:
                try:
                    trade_client.submit_order(
                        symbol_or_asset_id=symbol,
                        qty=float(pos.qty),
                        side='sell',
                        type='market',
                        time_in_force='gtc'
                    )
                    audit_msg = f"LIVE_TRADE: Emergency stop-loss triggered, liquidated 100% of {symbol} (Loss: {gain*100:.2f}%)"
                    log_to_risk_audit(audit_msg)
                    logger.warning(audit_msg)
                except Exception as order_err:
                    logger.error(f"[Worker Order Error] Failed stop-loss execution on {symbol}: {order_err}")

def run_worker() -> None:
    """Main resilient daemon heartbeat loop."""
    logger.info("Worker service initiated with high-availability architecture.")
    
    while True:
        try:
            manifest = load_manifest()
            assets = manifest.get('assets', [])
            if assets:
                execute_beast_logic(assets)
            else:
                logger.warning("[Worker] Manifest evaluated empty or unreadable.")
        except Exception as loop_err:
            logger.error(f"[Worker Critical] Unhandled exception in execution loop: {loop_err}")

        # Operational heartbeat cadence
        time.sleep(60)

if __name__ == "__main__":
    run_worker()

