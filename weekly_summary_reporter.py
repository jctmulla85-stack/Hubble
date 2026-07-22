import pandas as pd
import os
from notifier import send_alert

def generate_weekly_report(ledger_path):
    if not os.path.exists(ledger_path):
        send_alert("❌ REPORTER ERROR: Ledger file not found.")
        return

    try:
        df = pd.read_json(ledger_path, lines=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        last_week = df[df['timestamp'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))]

        # Build message
        msg = f"📊 **Weekly Business Summary**\n"
        msg += f"Total Trades: {len(last_week)}\n"
        msg += f"Total Tax Due: €{last_week['tax_due'].sum():.2f}"

        # Smart detection of PnL/Fee columns
        if 'pnl' in df.columns and 'fee' in df.columns:
            msg += f"\nNet PnL: €{last_week['pnl'].sum():.2f}"
            msg += f"\nTotal Fees: €{last_week['fee'].sum():.2f}"
        else:
            msg += "\n⚠️ Info: PnL/Fee tracking is currently inactive."

        send_alert(msg)
        print("Report sent successfully.")

    except Exception as e:
        send_alert(f"❌ REPORTER ERROR: {str(e)}")

if __name__ == "__main__":
    generate_weekly_report('/home/Mulla85/tax_ledger.json')
