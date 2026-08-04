import os
import logging
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass, AssetStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("execution.universe")

def get_tradable_equity_assets():
    api_key = os.getenv('ALPACA_KEY_APEX_001') or os.getenv('APCA_API_KEY_ID')
    secret_key = os.getenv('ALPACA_SECRET_APEX_001') or os.getenv('APCA_API_SECRET_KEY')
    paper_mode = os.getenv('BOT_MODE', 'PAPER').upper() == 'PAPER'
    
    client = TradingClient(api_key, secret_key, paper=paper_mode)
    
    # Request all active US equity assets available for trading, excluding crypto
    search_params = GetAssetsRequest(
        status=AssetStatus.ACTIVE,
        asset_class=AssetClass.US_EQUITY
    )
    
    assets = client.get_all_assets(search_params)
    tradable_symbols = [asset.symbol for asset in assets if asset.tradable]
    logger.info(f"[Universe Loaded] Retrieved {len(tradable_symbols)} tradable non-crypto equity assets from Alpaca.")
    return tradable_symbols

if __name__ == "__main__":
    symbols = get_tradable_equity_assets()
    print("Sample symbols:", symbols[:10])
