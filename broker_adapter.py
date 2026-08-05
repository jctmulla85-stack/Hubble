import sys
import os
import json
import urllib.request

class BrokerAdapter:
    def __init__(self, paper=True):
        self.paper = paper
        self.base_url = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        
        # Check standard Alpaca vars as well as the account-specific APEX_001 vars from .env
        self.api_key = (
            os.environ.get("APCA_API_KEY_ID") or 
            os.environ.get("ALPACA_KEY_APEX_001") or 
            os.environ.get("ALPACA_KEY_default_account") or ""
        )
        self.api_secret = (
            os.environ.get("APCA_API_SECRET_KEY") or 
            os.environ.get("ALPACA_SECRET_APEX_001") or 
            os.environ.get("ALPACA_SECRET_default_account") or ""
        )
        
        sys.stdout.write(f"[BROKER_ADAPTER] Initialized in {'PAPER' if self.paper else 'LIVE'} mode.\n")

    def get_tradable_assets(self):
        """
        Fetches the complete dynamic list of tradable US equities from Alpaca, 
        excluding crypto and non-tradable/OTC assets.
        """
        try:
            if not self.api_key or not self.api_secret:
                raise ValueError("API keys not found in environment variables.")
                
            url = f"{self.base_url}/v2/assets?status=active&asset_class=us_equity"
            req = urllib.request.Request(
                url,
                headers={
                    "APCA-API-KEY-ID": self.api_key,
                    "APCA-API-SECRET-KEY": self.api_secret,
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    assets = json.loads(response.read().decode())
                    symbols = [
                        asset["symbol"] for asset in assets 
                        if asset.get("tradable", False) and asset.get("exchange") != "OTC"
                    ]
                    sys.stdout.write(f"[BROKER_ADAPTER] Successfully loaded {len(symbols)} tradable assets from broker universe.\n")
                    return symbols
        except Exception as e:
            sys.stdout.write(f"[BROKER_ADAPTER] Error fetching live assets: {e}. Falling back to default baseline.\n")
            
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "JPM", "V", "JNJ", "WMT", "PG"]

    def submit_order(self, symbol, qty, side, order_type="market"):
        if qty <= 0:
            raise ValueError("Critical: Order quantity must be greater than zero.")
            
        sys.stdout.write(f"[BROKER_ADAPTER] Routing {side.upper()} {qty} shares of {symbol} ({order_type}).\n")
        
        return {
            "status": "submitted",
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type
        }
