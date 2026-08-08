import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from engine import SelfHealingEngine
from volatility_guard import VolatilityGuard
from order_executor import OrderExecutor
from asset_loader import AssetLoader

logging.basicConfig(
    filename="trading_engine_ledger.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class ProductionRunner:
    def __init__(self, max_workers=8, batch_size=100, target_capital_per_trade=100.0, min_share_price=5.0, max_sector_concentration=3):
        api_key = os.getenv("ALPACA_KEY_APEX_001")
        secret_key = os.getenv("ALPACA_SECRET_APEX_001")
        
        self.trading_client = TradingClient(api_key, secret_key, paper=True)
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        
        self.engine = SelfHealingEngine(self.trading_client)
        self.guard = VolatilityGuard(max_allowable_spread_pct=0.015)
        self.executor = OrderExecutor(self.trading_client, default_notional_usd=target_capital_per_trade)
        
        loader = AssetLoader(self.trading_client)
        self.universe = loader.get_tradable_equities()
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.min_share_price = min_share_price
        
        # Risk & Correlation Control State
        self.max_sector_concentration = max_sector_concentration
        self.active_positions_sector_count = {} # Tracks count per sector to prevent correlation clustering
        self._sync_current_positions()

    def _sync_current_positions(self):
        try:
            positions = self.trading_client.get_all_positions()
            for p in positions:
                # Basic sector tracking placeholder or asset asset-class grouping
                sector = getattr(p, 'asset_class', 'us_equity')
                self.active_positions_sector_count[sector] = self.active_positions_sector_count.get(sector, 0) + 1
        except Exception as e:
            logging.error(f"[CORRELATION SYNC ERROR] Failed to fetch active positions: {e}")

    def fetch_quotes_batch(self, symbols_chunk):
        try:
            req = StockLatestQuoteRequest(symbol_or_symbols=symbols_chunk)
            res = self.data_client.get_stock_latest_quote(req)
            quotes = {}
            for sym in symbols_chunk:
                if sym in res:
                    q = res[sym]
                    quotes[sym] = {"bid": float(q.bid_price), "ask": float(q.ask_price)}
            return quotes
        except Exception as e:
            logging.error(f"[BATCH ERROR] Failed fetching quote chunk: {e}")
            return {}

    def process_symbol(self, symbol, quote):
        mid_price = (quote["bid"] + quote["ask"]) / 2.0
        if mid_price < self.min_share_price:
            return  # Exclude low-priced dust/penny stocks
            
        if not self.guard.evaluate_market_conditions(symbol, quote["bid"], quote["ask"]):
            return
            
        # Correlation / Concentration Check
        # Prevents piling into too many simultaneous positions within the same segment
        default_sector = "us_equity"
        current_sector_load = self.active_positions_sector_count.get(default_sector, 0)
        if current_sector_load >= self.max_sector_concentration:
            logging.info(f"[{symbol}] Skipped due to correlation/sector concentration limit ({current_sector_load} active).")
            return
            
        logging.info(f"[{symbol}] Passed price, volatility, and correlation guards. Routing execution order.")
        order = self.executor.submit_buy_order(symbol)
        if order:
            self.active_positions_sector_count[default_sector] = current_sector_load + 1

    def execute_scan(self):
        logging.info("Initiating high-performance batched equity universe scan with anti-dust and correlation filters...")
        chunks = [self.universe[i:i + self.batch_size] for i in range(0, len(self.universe), self.batch_size)]
        
        for chunk in chunks:
            quotes = self.engine.safe_api_call(self.fetch_quotes_batch, chunk)
            if not quotes:
                continue
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [
                    executor.submit(self.process_symbol, sym, quotes[sym]) 
                    for sym in quotes
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as exc:
                        logging.error(f"[WORKER ERROR] Symbol execution generated exception: {exc}")

if __name__ == "__main__":
    runner = ProductionRunner()
    runner.execute_scan()
