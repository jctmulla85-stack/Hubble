import json
import os

# Define the path to your governance policy
POLICY_FILE = '/home/Mulla85/QuantBot/governance/governance_policy.json'

def test_load_governance():
    print("--- Governance Fail-Safe Test ---")

    if not os.path.exists(POLICY_FILE):
        print("CRITICAL ERROR: Policy file missing.")
        return

    try:
        with open(POLICY_FILE, 'r') as f:
            policy = json.load(f)

        # Test 1: Check for critical safety values
        max_trade = policy.get('max_trade_size', 0)

        if not isinstance(max_trade, (int, float)) or max_trade <= 0:
            raise ValueError(f"DANGEROUS POLICY: max_trade_size is {max_trade}. Must be > 0.")

        print("TEST PASSED: Governance policy is logically sound.")
        print(f"Policy loaded: Max Trade Size = {max_trade}")

    except Exception as e:
        print(f"TEST FAILED: Governance block triggered! System would halt. Error: {e}")

if __name__ == "__main__":
    test_load_governance()
