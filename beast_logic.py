import json
import datetime

# Configuration for your tax records and trade execution
LEDGER_FILE = '/home/Mulla85/tax_ledger.json'
MANIFEST_FILE = '/home/Mulla85/orders_manifest.json'

def log_trade(asset_symbol, pnl, fee, tax_due):
    """Logs trade data into your ledger for future tax auditing."""
    trade_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "asset": asset_symbol,
        "pnl": float(pnl),
        "fee": float(fee),
        "tax_rate_applied": 0.125,  # Corrected to 12.5% for Irish Corp Tax
        "tax_due": float(tax_due)
    }
    with open(LEDGER_FILE, 'a') as f:
        f.write(json.dumps(trade_entry) + '\n')
    print(f"✅ Trade logged for: {asset_symbol}")

def run_all_assets():
    """Main execution loop for your automated trading system."""
    # Logic: Load active assets directly from broker API or manifest
    with open(MANIFEST_FILE, 'r') as f:
        data = json.load(f)
        assets = data.get('assets', [])

    for item in assets:
        symbol = item['symbol']

        # --- Logic Simulation: Replace with your actual Alpaca API calls ---
        pnl = 100.00    # Placeholder: Replace with live PnL fetch
        fee = 1.00      # Placeholder: Replace with live fee fetch

        # Corrected tax calculation: (PnL - Fee) * 12.5%
        tax = (pnl - fee) * 0.125

        log_trade(symbol, pnl, fee, tax)

if __name__ == "__main__":
    run_all_assets()
