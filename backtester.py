import pandas as pd
from risk_engine import calculate_atr, get_dynamic_qty

def run_simulation(data_file):
    df = pd.read_csv(data_file)
    equity = 100000

    print(f"{'Day':<5} | {'ATR':<8} | {'Suggested Qty'}")

    for i in range(14, len(df)):
        window = df.iloc[i-14:i]
        atr = calculate_atr(window)
        qty = get_dynamic_qty(equity, 0.01, atr, df['close'].iloc[i])
        print(f"{i:<5} | {atr or 0:<8.2f} | {qty}")

if __name__ == "__main__":
    # Ensure you have a 'market_data.csv' file in the same folder
    run_simulation('market_data.csv')
