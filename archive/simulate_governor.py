import json
from collections import Counter

# Define the absolute path to your data
INPUT_FILE = "/home/Mulla85/QuantBot/trading_audit_parsed.jsonl"

def get_veto_category(message):
    """Categorizes the error type for better reporting."""
    msg = message.lower()
    if "timeout" in msg or "latency" in msg:
        return "LATENCY_ISSUE"
    elif "insufficient" in msg or "funds" in msg:
        return "ACCOUNT_ISSUE"
    elif "error" in msg:
        return "GENERAL_ERROR"
    return None

def run_governor_simulation():
    total_events = 0
    veto_count = 0
    categories = Counter()

    try:
        with open(INPUT_FILE, "r") as f:
            for line in f:
                if not line.strip():
                    continue

                total_events += 1
                entry = json.loads(line)
                message = entry.get('message', '')

                # Check for veto
                category = get_veto_category(message)
                if category:
                    veto_count += 1
                    categories[category] += 1

        # Display Report
        print("-" * 40)
        print("ENTERPRISE GOVERNOR: SIMULATION REPORT")
        print("-" * 40)
        print(f"Total Events Processed: {total_events}")
        print(f"Total Vetoes Triggered: {veto_count}")

        if total_events > 0:
            approval_rate = ((total_events - veto_count) / total_events) * 100
            print(f"Approval Rate:          {approval_rate:.2f}%")

        if veto_count > 0:
            print("\nBreakdown by Category:")
            for cat, count in categories.items():
                print(f" - {cat}: {count}")
        print("-" * 40)

    except FileNotFoundError:
        print(f"Error: Could not find log file at {INPUT_FILE}")
    except json.JSONDecodeError:
        print("Error: Log file contains malformed JSON.")

if __name__ == "__main__":
    run_governor_simulation()
