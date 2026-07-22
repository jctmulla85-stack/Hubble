import unittest
from governance.governor import Governor
from governance.kill_switch import DrawdownProtector
import pandas as pd

class TestSafetyOrgans(unittest.TestCase):
    def setUp(self):
        self.gov = Governor()
        self.protector = DrawdownProtector(max_daily_loss=50.0)

    def test_governor_blocks_high_volatility(self):
        # Create extreme market data (volatility > 2.0)
        df = pd.DataFrame({'high': [100.0], 'low': [97.5]}) # Volatility = 2.5
        signal = "BUY"
        is_safe = self.gov.validate_signal(signal, df)
        self.assertFalse(is_safe, "Governor should block trades during high volatility.")

    def test_kill_switch_triggers_on_excessive_loss(self):
        # Simulate a $60 loss against a $50 limit
        current_pnl = -60.0
        is_safe = self.protector.is_safe(current_pnl)
        self.assertFalse(is_safe, "Kill-switch should trigger on excessive drawdown.")

if __name__ == "__main__":
    unittest.main()
