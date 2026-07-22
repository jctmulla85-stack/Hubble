import json

class RiskManager:
    def __init__(self, event_bus, max_pos_size=1000):
        self.bus = event_bus
        self.max_pos_size = max_pos_size
        self.bus.subscribe("STRATEGY_SIGNAL", self.validate_signal)

    def validate_signal(self, event):
        payload = event["payload"]
        if payload.get("quantity", 0) <= self.max_pos_size:
            print(f"[Risk] Approved: {payload.get('asset')}")
            self.bus.publish("ORDER_REQUEST", payload)
        else:
            print(f"[Risk] REJECTED: {payload.get('asset')} - Size exceeds limit.")

class ShadowExecutor:
    def __init__(self, event_bus, mode="SHADOW"):
        self.bus = event_bus
        self.mode = mode
        self.bus.subscribe("ORDER_REQUEST", self.route_order)

    def route_order(self, event):
        payload = event["payload"]
        if self.mode == "SHADOW":
            print(f"[SHADOW] Simulation: {payload.get('side')} {payload.get('quantity')} {payload.get('asset')}")
            self.bus.publish("FILL_CONFIRMED", {"status": "FILLED_SIM", **payload})
        else:
            print(f"[LIVE] Executing real trade on Alpaca!")
            self.bus.publish("FILL_CONFIRMED", {"status": "FILLED_LIVE", **payload})

class RegimeObserver:
    def __init__(self, event_bus):
        self.bus = event_bus
        self.current_regime = "NEUTRAL"

    def analyze_data(self, market_data):
        vol = market_data.get('volatility', 0)
        new_regime = "TRENDING" if vol < 0.02 else "VOLATILE"
        if new_regime != self.current_regime:
            self.current_regime = new_regime
            print(f"[Observer] Regime Shift: {self.current_regime}")
            self.bus.publish("REGIME_CHANGE", {"regime": self.current_regime})

class TaxAuditModule:
    def __init__(self, event_bus, rules_path="tax_rules.json"):
        self.bus = event_bus
        self.rules_path = rules_path
        self.bus.subscribe("FILL_CONFIRMED", self.record_trade)

    def get_current_tax_rules(self):
        try:
            with open(self.rules_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"capital_gains_tax_rate": 0.33, "jurisdiction": "Ireland"}

    def record_trade(self, event):
        rules = self.get_current_tax_rules()
        payload = event["payload"]
        profit = payload.get("profit", 0)
        tax_liability = profit * rules.get("capital_gains_tax_rate", 0.33)

        trade_record = {
            "timestamp": event["timestamp"],
            "asset": payload.get("asset"),
            "tax_rate_applied": rules.get("capital_gains_tax_rate"),
            "tax_due": round(tax_liability, 2)
        }
        with open("tax_ledger.json", "a") as f:
            f.write(json.dumps(trade_record) + "\n")
        print(f"[TaxAudit] Recorded trade. Tax Due: {trade_record['tax_due']}")
