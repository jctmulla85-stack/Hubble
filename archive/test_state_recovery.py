import json
import os

# Define the path to your state memory
STATE_FILE = '/home/Mulla85/QuantBot/memory/system_state.json'

def verify_state():
    print("--- Million Dollar State Recovery Test ---")

    if not os.path.exists(STATE_FILE):
        print(f"CRITICAL ERROR: State file not found at {STATE_FILE}")
        return

    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)

        print("System State Loaded Successfully.")
        print(f"Last Known Market Status: {state.get('market_status', 'UNKNOWN')}")
        print(f"Open Positions Count: {len(state.get('open_positions', []))}")
        print(f"Governor Status: {state.get('governor_active', False)}")

        # Logic check: If the governor isn't active, the system shouldn't trade
        if not state.get('governor_active', False):
            print("TEST PASSED: System safely initialized in 'Governor Inactive' mode.")
        else:
            print("TEST WARNING: System initialized with active trading. Ensure this is intentional.")

    except Exception as e:
        print(f"TEST FAILED: Could not parse state file. Error: {e}")

if __name__ == "__main__":
    verify_state()
