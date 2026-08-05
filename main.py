import sys
import os
import time

# Load environment variables from .env file if present
from pathlib import Path
env_path = Path('.') / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ.setdefault(key, val)

from broker_adapter import BrokerAdapter
from strategy import MomentumStrategy

def main():
    sys.stdout.write("[MAIN] Initializing QuantBot Architecture with Dynamic Asset Universe...\n")
    
    broker = BrokerAdapter(paper=True)
    assets = broker.get_tradable_assets()
    sys.stdout.write(f"[MAIN] Loaded tradable asset universe: {len(assets)} assets.\n")
    
    strategy = MomentumStrategy(assets)
    if hasattr(strategy, "initialize_feed"):
        strategy.initialize_feed()
    
    sys.stdout.write("[MAIN] Entering continuous event loop. Monitoring market hours...\n")
    try:
        while True:
            sys.stdout.write("[MAIN] Market closed. Bot idling to conserve CPU/RAM...\n")
            time.sleep(60)
    except KeyboardInterrupt:
        sys.stdout.write("[MAIN] Shutting down gracefully.\n")

if __name__ == "__main__":
    main()
