import json
import csv
import sys
from datetime import datetime

def export_ledger_to_csv(json_file_path, csv_file_path):
    # Define headers required for Irish Revenue audit compliance
    headers = ["timestamp", "asset", "type", "quantity", "price_eur", "fees", "net_pnl_eur"]

    # Open the CSV file for writing
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()

        # Open the JSON Lines file and read it line by line
        with open(json_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # Ensure the line is not empty
                    try:
                        entry = json.loads(line)
                        writer.writerow({
                            "timestamp": entry.get("timestamp"),
                            "asset": entry.get("asset"),
                            "type": entry.get("type"),
                            "quantity": entry.get("quantity"),
                            "price_eur": entry.get("price_eur"),
                            "fees": entry.get("fees"),
                            "net_pnl_eur": entry.get("net_pnl_eur")
                        })
                    except json.JSONDecodeError as e:
                        print(f"Skipping malformed line: {e}")

# 1. Weekly Trigger Logic
# Monday is 0, Sunday is 6.
# This runs only on Sundays (6). Change '6' if you prefer a different day.
if datetime.today().weekday() != 6:
    sys.exit()

# 2. Execute the export
try:
    export_ledger_to_csv('/home/Mulla85/tax_ledger.json', '/home/Mulla85/tax_report_2026.csv')
    print("✅ Compliance report generated successfully.")
except Exception as e:
    print(f"❌ Error during export: {e}")
