from unittest.mock import MagicMock
from governance.gatekeeper import Gatekeeper

def test_diagnostic_logging():
    # Setup mocks
    mock_gov = MagicMock()
    mock_gov.is_halted = False
    mock_gov.current_regime = "TEST_MODE"
    mock_gov.calculate_position_size.return_value = 100
    mock_api = MagicMock()

    # Initialize
    gk = Gatekeeper(mock_gov, mock_api)

    # Trigger a test order
    order = {'price': 100, 'stop': 90, 'volume': 1000}
    gk.execute_order(order)

    print("Test executed. Check 'trading_diagnostics.jsonl' for the log entry.")

if __name__ == "__main__":
    test_diagnostic_logging()
