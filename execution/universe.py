import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetStatus

# Force load environment variables from .env
load_dotenv(override=True)

def get_tradable_equity_assets():
    api_key = os.getenv('ALPACA_KEY_APEX_001')
    secret_key = os.getenv('ALPACA_SECRET_APEX_001')
    paper_mode = os.getenv('BOT_MODE', 'PAPER').upper() == 'PAPER'
    
    client = TradingClient(api_key, secret_key, paper=paper_mode)
    
    search_params = GetAssetsRequest(
        status=AssetStatus.ACTIVE,
        asset_class='us_equity'
    )
    assets = client.get_all_assets(search_params)
    return [asset.symbol for asset in assets if asset.tradable]
