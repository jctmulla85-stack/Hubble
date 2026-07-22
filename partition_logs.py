import pandas as pd

def partition_data():
    try:
        # We use on_bad_lines='skip' to ignore rows that don't fit the format
        # If your log is tab-separated or uses a different delimiter, change sep=','
        df = pd.read_csv('trading_audit.log', on_bad_lines='skip', sep=',')

        if df.empty:
            print("[ERROR] Log file is empty or unreadable.")
            return

        split_idx = int(len(df) * 0.85)

        train_df = df.iloc[:split_idx]
        vault_df = df.iloc[split_idx:]

        train_df.to_csv('train.csv', index=False)
        vault_df.to_csv('vault.csv', index=False)

        print(f"[VAULT] Success: Partitioned {len(df)} trades.")
        print(f"Training: {len(train_df)} | Vault: {len(vault_df)}")

    except Exception as e:
        print(f"[ERROR] Could not parse log: {e}")

if __name__ == "__main__":
    partition_data()
