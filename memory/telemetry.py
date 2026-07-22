import json
from datetime import datetime
from pathlib import Path

class Telemetry:
    def __init__(self, state_manager, report_file="telemetry_report.json"):
        self.state_manager = state_manager
        self.report_path = Path(report_file)

    def generate_report(self):
        """Aggregates state into a diagnostic summary."""
        state = self.state_manager.state

        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "OPERATIONAL",
            "positions": state.get('positions', {}),
            "last_action": state.get('last_action', 'NONE'),
            "last_perception": state.get('last_perception', 'NONE'),
            "version": "1.0.0" # Allows you to track evolution as you upgrade
        }

        # Save the diagnostic snapshot
        with open(self.report_path, "w") as f:
            json.dump(report, f, indent=4)

        return report
