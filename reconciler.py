import os
import sys
import logging
from typing import Optional
import pandas as pd

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from notifier import send_alert
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

def reconcile_trades(ledger_path: str, broker_csv_path: str) -> None:
    """
    Reconciles internal JSON Lines trade ledger against an external broker CSV export.
    Identifies discrepancies, logs audit trails, and triggers notifications securely.
    """
    logger.info("[Reconciler] Initiating trade ledger vs broker statement reconciliation.")

    try:
        # 1. Defensive Path Validation
        if not os.path.exists(ledger_path):
            error_msg = f"[Reconciler Error] Internal ledger file missing at path: {ledger_path}"
            logger.error(error_msg)
            send_alert(error_msg)
            return

        if not os.path.exists(broker_csv_path):
            error_msg = f"[Reconciler Error] Broker CSV export missing at path: {broker_csv_path}"
            logger.error(error_msg)
            send_alert(error_msg)
            return

        # 2. Robust Data Loading
        try:
            ledger_df = pd.read_json(ledger_path, lines=True)
        except Exception as e:
            error_msg = f"[Reconciler Error] Failed to parse internal ledger JSON Lines: {e}"
            logger.error(error_msg)
            send_alert(error_msg)
            return

        try:
            broker_df = pd.read_csv(broker_csv_path)
        except Exception as e:
            error_msg = f"[Reconciler Error] Failed to parse broker CSV statement: {e}"
            logger.error(error_msg)
            send_alert(error_msg)
            return

        # 3. Schema & Column Validation
        required_ledger_col = 'transaction_id'
        required_broker_col = 'Broker_Trade_ID'

        if required_ledger_col not in ledger_df.columns:
            error_msg = f"[Reconciler Error] Missing required column '{required_ledger_col}' in ledger."
            logger.error(error_msg)
            send_alert(error_msg)
            return

        if required_broker_col not in broker_df.columns:
            error_msg = f"[Reconciler Error] Missing required column '{required_broker_col}' in broker statement."
            logger.error(error_msg)
            send_alert(error_msg)
            return

        # 4. Standardization
        ledger_df[required_ledger_col] = ledger_df[required_ledger_col].astype(str)
        broker_df[required_broker_col] = broker_df[required_broker_col].astype(str)

        # 5. Matching Logic (Outer Join with indicator)
        reconciled = pd.merge(
            ledger_df,
            broker_df,
            left_on=required_ledger_col,
            right_on=required_broker_col,
            how='outer',
            indicator=True
        )

        # 6. Filter for Discrepancies
        breaks = reconciled[reconciled['_merge'] != 'both']

        if not breaks.empty:
            break_file = os.path.join(BASE_DIR, 'reconciliation_breaks.csv')
            breaks.to_csv(break_file, index=False)
            msg = f"⚠️ RECONCILIATION BREAKS FOUND: {len(breaks)} discrepancies detected. Saved to {break_file}."
            logger.warning(msg)
            print(msg)
            send_alert(msg)
        else:
            msg = "✅ Reconciliation Complete: All internal trades matched successfully with broker records."
            logger.info(msg)
            print(msg)
            send_alert(msg)

    except Exception as e:
        error_msg = f"[Reconciler Critical] Unhandled exception during reconciliation cycle: {str(e)}"
        logger.error(error_msg)
        print(error_msg)
        send_alert(error_msg)

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LEDGER = os.path.join(BASE_DIR, 'tax_ledger.json')
    BROKER_EXPORT = os.path.join(BASE_DIR, 'broker_statement.csv')
    
    reconcile_trades(LEDGER, BROKER_EXPORT)

