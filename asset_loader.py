import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass, AssetStatus

class AssetLoader:
    def __init__(self, trading_client):
        self.client = trading_client

    def get_tradable_equities(self):
        search_params = GetAssetsRequest(
            asset_class=AssetClass.US_EQUITY,
            status=AssetStatus.ACTIVE
        )
        assets = self.client.get_all_assets(search_params)
        tradable_symbols = [asset.symbol for asset in assets if asset.tradable and "/" not in asset.symbol]
        print(f"[ASSET LOADER] Loaded {len(tradable_symbols)} active, tradable US equities (Crypto excluded).")
        return tradable_symbols

if __name__ == "__main__":
    client = TradingClient(os.getenv("ALPACA_KEY_APEX_001"), os.getenv("ALPACA_SECRET_APEX_001"), paper=True)
    loader = AssetLoader(client)
    loader.get_tradable_equities()
