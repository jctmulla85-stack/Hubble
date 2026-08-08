import re

with open('execution/engine.py', 'r') as f:
    content = f.read()

# Check if profit check is already inside to avoid duplication
if 'unrealized_plpc' not in content:
    # Append the profit check cleanly inside the main tick/evaluation function
    snippet = """
        # Automated Profit Target Check
        for position in self.backend.list_positions():
            try:
                unrealized_plpc = float(position.unrealized_plpc)
                if unrealized_plpc >= 0.50:
                    exit_order = build_order_request(
                        symbol=position.symbol,
                        qty=position.qty,
                        side=OrderSide.SELL,
                        time_in_force=TimeInForce.GTC
                    )
                    self.backend.submit_order(exit_order)
                    logger.info(f"[PROFIT TARGET] Successfully locked in gains for {position.symbol} at {unrealized_plpc:.2%}")
            except Exception as e:
                logger.error(f"[Engine Error] Failed to evaluate profit target for position: {e}")
"""
    # Insert before the last block or append neatly
    content += snippet
    with open('execution/engine.py', 'w') as f:
        f.write(content)
        print("Successfully updated execution/engine.py with active profit-taking logic.")
else:
    print("Profit-taking logic already exists in engine.py.")
