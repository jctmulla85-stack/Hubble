import json
from governance.governor import EnterpriseGovernor # Your new logic

# 1. Load your historical data
log_file = "/home/Mulla85/logs/trading_audit.log"
governor = EnterpriseGovernor()

def replay_logs():
    with open(log_file, "r") as f:
        for line in f:
            # Assume your log lines are JSON objects
            event = json.loads(line)

            # 2. Let the Governor "veto" or "approve" the event
            decision = governor.evaluate(event)

            print(f"Event: {event['type']} | Governor Decision: {decision}")

if __name__ == "__main__":
    replay_logs()
