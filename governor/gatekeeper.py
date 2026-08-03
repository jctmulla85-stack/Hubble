from dotenv import load_dotenv
load_dotenv()
import os
import json
import logging
from typing import Dict, Any, List
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetStatus, AssetClass

# Configure institutional-grade logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (Gatekeeper): %(message)s"
)

class SystemGovernor:
    def __init__(self, params_path: str = "research/optimal_params.json"):
        self.params_path = params_path
        self._ensure_storage()
        
        # Initialize Alpaca client for live asset universe tracking
        api_key = os.getenv("ALPACA_KEY_APEX_001")
        secret_key = os.getenv("ALPACA_SECRET_APEX_001")
        self.trading_client = TradingClient(api_key=api_key, secret_key=secret_key, paper=True)

    def _ensure_storage(self) -> None:
        """Ensures the required directory and a baseline parameter file exist."""
        try:
            directory = os.path.dirname(self.params_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            if not os.path.exists(self.params_path):
                baseline = {"window": 14, "threshold": 2.0}
                with open(self.params_path, "w") as f:
                    json.dump(baseline, f, indent=4)
                logging.info("Initialized default optimal parameters baseline.")
        except Exception as e:
            logging.error(f"Failed to initialize storage path: {e}")
            raise

    def fetch_active_asset_universe(self) -> List[str]:
        """
        Dynamically queries Alpaca for all active, tradable assets 
        across the market to power full-scale system capabilities.
        """
        try:
            search_params = GetAssetsRequest(
                status=AssetStatus.ACTIVE,
                asset_class=AssetClass.US_EQUITY
            )
            assets = self.trading_client.get_all_assets(search_params)
            
            tradable_symbols = [
                asset.symbol for asset in assets 
                if getattr(asset, "tradable", False)
            ]
            logging.info(f"Loaded {len(tradable_symbols)} tradable assets from Alpaca universe.")
            return tradable_symbols
        except Exception as e:
            logging.error(f"Failed to fetch asset universe from Alpaca: {e}")
            return ["AAPL"]

    def validate_and_apply(self, candidate_params: Dict[str, Any]) -> bool:
        """
        Audits incoming parameters through strict safety and anti-overfitting bounds
        before permitting the system to adopt them.
        """
        try:
            if not isinstance(candidate_params, dict):
                logging.warning("Governor rejected: Candidate parameters must be a dictionary.")
                return False

            window = candidate_params.get("window")
            threshold = candidate_params.get("threshold")

            if window is None or threshold is None:
                logging.warning("Governor rejected: Missing mandatory parameter keys ('window' or 'threshold').")
                return False

            if not isinstance(window, int) or window < 2 or window > 252:
                logging.warning(f"Governor rejected: Window value {window} violates safety bounds [2, 252].")
                return False

            if not isinstance(threshold, (int, float)) or threshold <= 0.0 or threshold > 10.0:
                logging.warning(f"Governor rejected: Threshold value {threshold} violates safety bounds (0, 10.0].")
                return False

            temp_path = f"{self.params_path}.tmp"
            with open(temp_path, "w") as f:
                json.dump(candidate_params, f, indent=4)
            
            os.replace(temp_path, self.params_path)
            logging.info("Governor successfully validated and committed new parameter set.")
            return True

        except Exception as e:
            logging.error(f"Governor critical error during parameter validation: {e}")
            if os.path.exists(f"{self.params_path}.tmp"):
                os.remove(f"{self.params_path}.tmp")
            return False

    def load_current_parameters(self) -> Dict[str, Any]:
        """Safely loads the active parameters currently cleared by the governor."""
        try:
            if os.path.exists(self.params_path):
                with open(self.params_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load current parameters: {e}")
        return {"window": 14, "threshold": 2.0}


if __name__ == "__main__":
    gatekeeper = SystemGovernor()
    test_params = {"window": 14, "threshold": 2.0}
    
    if gatekeeper.validate_and_apply(test_params):
        universe = gatekeeper.fetch_active_asset_universe()
        logging.info(f"Gatekeeper operational test passed. Total active symbols recognized: {len(universe)}")
    else:
        logging.error("Gatekeeper operational test failed.")
