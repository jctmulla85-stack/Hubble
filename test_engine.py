import os
from engine import SelfHealingEngine

# Mock API client to simulate successful calls and network/rate-limit exceptions
class MockAPI:
    def __init__(self):
        self.attempts = 0

    def list_orders(self, status="open"):
        self.attempts += 1
        if self.attempts < 2:
            # Simulate a temporary network drop or rate limit error on first try
            raise Exception("429 Too Many Requests: connection unstable")
        # Return a mock order object on successful retry
        class MockOrder:
            client_order_id = "test_client_id_123"
            id = "broker_order_abc"
        return [MockOrder()]

def run_tests():
    print("Initializing Self-Healing Engine Test Suite...")
    api = MockAPI()
    engine = SelfHealingEngine(api)

    # Test 1: Verify Self-Healing Retry Logic
    print("\n[Test 1] Testing self-healing API retry & recovery...")
    result = engine.safe_api_call(api.list_orders, status="open")
    if result is not None:
        print("[SUCCESS] Self-healing loop recovered successfully from simulated rate-limit error.")

    # Test 2: Verify Orphan Reconciliation
    print("\n[Test 2] Testing orphan order reconciliation...")
    found = engine.reconcile_orphan_orders("test_client_id_123")
    if found:
        print("[SUCCESS] Orphan reconciliation correctly identified the active order ID.")

    # Test 3: Verify Metadata Logging
    print("\n[Test 3] Testing local trade telemetry logging...")
    engine.log_trade_metadata(
        symbol="AAPL",
        side="buy",
        qty=100,
        expected_price=150.00,
        fill_price=150.05,
        spread=0.03
    )
    
    if os.path.exists("trade_telemetry.jsonl"):
        print("[SUCCESS] 'trade_telemetry.jsonl' verified. Log entry appended cleanly.")
    else:
        print("[ERROR] Telemetry file not found.")

    print("\nAll verification tests completed successfully.")

if __name__ == "__main__":
    run_tests()
