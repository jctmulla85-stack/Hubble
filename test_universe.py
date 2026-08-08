import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

load_dotenv()
api = tradeapi.REST(
    os.getenv('ALPACA_KEY_APEX_001'), 
    os.getenv('ALPACA_SECRET_APEX_001'), 
    base_url='https://paper-api.alpaca.markets'
)

assets = api.list_assets(status='active', asset_class='us_equity')
universe = [asset.symbol for asset in assets if asset.tradable]
print(f"Total tradable symbols: {len(universe)}")
print(f"Sample symbols: {universe[:10]}")
