# ~/QuantBot/test_connection.py
from alpaca.trading.client import TradingClient
from config import Config

# Initialize client using Config attributes
client = TradingClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, paper=True)

def test_api():
    try:
        account = client.get_account()
        print(f"Connection Successful!")
        print(f"Buying Power: ${account.buying_power}")
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    test_api()
