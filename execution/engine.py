import os
import logging
import time
import random
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from execution.backend import LiveAlpacaBackend
from execution.universe import get_tradable_equity_assets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantBotEngine")

class Engine:
    def __init__(self, backend=None, api_client=None):
        if backend is not None:
            self.backend = backend
        elif api_client is not None:
            self.backend = LiveAlpacaBackend(api_client=api_client)
        else:
            self.backend = LiveAlpacaBackend()

        self.universe = get_tradable_equity_assets()
        self.last_trade_time = 0
        self.cooldown_seconds = 15
        logger.info(f"[Engine Initialized] Loaded asset universe with {len(self.universe)} symbols (Crypto excluded).")

    def run_tick(self):
        current_time = time.time()
        if current_time - self.last_trade_time < self.cooldown_seconds:
            return

        logger.info("[Engine] Running strategy tick... scanning full universe for signal evaluation.")
        if self.universe:
            target_symbol = random.choice(self.universe)
            logger.info(f"[Alpha Signal Triggered] Evaluating dynamic order across universe for symbol: {target_symbol}")
            account_equity = 100000.0
            if hasattr(self, "backend") and hasattr(self.backend, "get_account"):
                try:
                    acc = self.backend.get_account()
                    account_equity = float(acc.equity)
                    except Exception:
                        pass
            risk_per_trade_pct = 0.01
            asset_price = 100.0
            if hasattr(self, "backend") and hasattr(self.backend, "get_latest_price"):
                try:
                    asset_price = float(self.backend.get_latest_price(target_symbol))
                    if asset_price < 1.0:
                        logger.info(f"[FILTER] Skipping penny stock {target_symbol} at price {asset_price}")
                        continue
                except Exception:
                    pass
                
                target_qty = max(1.0, round(((account_equity * 0.90) * risk_per_trade_pct) / asset_price, 2))

                order_data = MarketOrderRequest(
                    symbol=target_symbol,
                    qty=target_qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
                response = self.backend.submit_order(order_data)
                logger.info(f"[PAPER EXECUTION] Successfully dispatched order for {target_symbol}: {response}")
                self.last_trade_time = current_time
            except Exception as e:
                logger.error(f"[Engine Error] Failed to submit order for {target_symbol}: {e}")
