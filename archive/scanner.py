import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi

# Secure Imports from internal modules
from logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

# Load environment variables securely
load_dotenv()

MANIFEST_PATH = 'trading_system.jsonl'
TMP_PATH = 'trading_system.tmp'

def get_assets() -> List[Dict[str, Any]]:
    """
    Connects to the Alpaca REST API securely using environment credentials
    and queries active, tradable US equities dynamically.
    """
    logger.info("[Scanner] Initializing Alpaca REST client connection.")

    try:
        key_id = os.getenv('ALPACA_KEY_APEX_001')
        secret_key = os.getenv('ALPACA_SECRET_APEX_001')
        base_url = os.getenv('APCA_API_BASE_URL', 'https://paper-api.alpaca.markets')

        if not key_id or not secret_key:
            logger.error("[Scanner Error] Missing Alpaca API credentials in environment configuration.")
            return []

        api = tradeapi.REST(
            key_id=key_id,
            secret_key=secret_key,
            base_url=base_url
        )

        active_assets: List[Dict[str, Any]] = []
        
        logger.info("[Scanner] Querying broker for active US equity assets...")
        equity_assets = api.list_assets(status='active', asset_class='us_equity')

        for asset in equity_assets:
            if getattr(asset, 'tradable', False):
                active_assets.append({
                    'symbol': asset.symbol,
                    'vol_proxy': 1.0
                })

        logger.info(f"[Scanner] Successfully fetched {len(active_assets)} tradable assets.")
        return active_assets

    except Exception as e:
        logger.error(f"[Scanner Critical] Exception encountered while fetching assets from broker: {e}")
        return []

def update_assignments() -> None:
    """
    Performs an atomic write pattern to update the asset manifest manifest safely,
    preventing file corruption during system reloads.
    """
    logger.info("[Scanner] Starting manifest update cycle.")

    try:
        assets = get_assets()
        if not assets:
            logger.warning("[Scanner Warning] Asset list retrieved is empty. Manifest update aborted to protect state.")
            return

        # Atomic write pattern: Write to temp file first
        with open(TMP_PATH, 'w') as f:
            json.dump({'assets': assets}, f, indent=2)

        # Atomic rename replaces target instantly
        os.rename(TMP_PATH, MANIFEST_PATH)
        
        success_msg = f"[Scanner] Successfully updated {MANIFEST_PATH} with {len(assets)} active assets."
        logger.info(success_msg)
        print(success_msg)

    except Exception as e:
        error_msg = f"[Scanner Critical] Fatal error during manifest update: {e}"
        logger.error(error_msg)
        print(error_msg)
        
        # Cleanup temp file if it exists
        if os.path.exists(TMP_PATH):
            try:
                os.remove(TMP_PATH)
            except Exception:
                pass

if __name__ == "__main__":
    update_assignments()
