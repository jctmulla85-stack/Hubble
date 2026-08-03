import json
import urllib.request
import urllib.error

class BrokerHandshake:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://paper-api.alpaca.markets"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")

    def connect_and_discover(self) -> dict:
        url = f"{self.base_url}/v2/account"
        
        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Accept": "application/json"
        }

        req = urllib.request.Request(url, headers=headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    
                    # Extract key account parameters for the constraint mesh
                    account_profile = {
                        "status": data.get("status"),
                        "account_number": data.get("account_number"),
                        "equity": float(data.get("equity", 0.0)),
                        "buying_power": float(data.get("buying_power", 0.0)),
                        "multiplier": data.get("multiplier"),
                        "currency": data.get("currency", "USD"),
                        "daytrading_count": data.get("daytrading_count", 0)
                    }
                    print(f"[Handshake] Successfully connected to gateway. Account Status: {account_profile['status']} | Equity: ${account_profile['equity']}")
                    return account_profile
                else:
                    print(f"[Handshake] Gateway returned non-200 status: {response.status}")
                    return {}
                    
        except urllib.error.HTTPError as e:
            print(f"[Handshake] HTTP Error during auto-discovery: {e.code} - {e.reason}")
            return {}
        except Exception as e:
            print(f"[Handshake] Connection failure: {e}")
            return {}
