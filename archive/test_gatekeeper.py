from governance.gatekeeper import Gatekeeper
from unittest.mock import MagicMock

def test_gatekeeper_veto():
    # 1. Setup Mocks
    mock_gov = MagicMock()
    mock_api = MagicMock()

    # 2. Setup the "Gatekeeper" (your new file)
    gk = Gatekeeper(mock_gov, mock_api)

    # 3. Scenario: Governor is Halted (Should be rejected)
    mock_gov.is_halted = True
    order = {'price': 100, 'stop': 90, 'volume': 1000}

    result = gk.execute_order(order)

    if result is None:
        print("TEST PASSED: Gatekeeper successfully blocked order while halted.")
    else:
        print("TEST FAILED: Gatekeeper allowed order through a halted system!")

    # 4. Scenario: Governor is active, but risk is high (Should be rejected)
    mock_gov.is_halted = False
    mock_gov.calculate_position_size.return_value = 0 # Governor says 0 units

    result = gk.execute_order(order)

    if result is None:
        print("TEST PASSED: Gatekeeper successfully blocked unsafe order.")
    else:
        print("TEST FAILED: Gatekeeper allowed an unsafe order!")

if __name__ == "__main__":
    test_gatekeeper_veto()
