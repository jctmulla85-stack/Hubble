import logging

class Reconciler:
    def __init__(self, governor):
        self.governor = governor
        # Setup logging specifically for reconciliation events
        self.logger = logging.getLogger("Reconciler")

    def verify_state(self, internal_balance, broker_balance):
        """
        Compares local records against broker truth.
        Uses a 0.01% tolerance threshold for floating-point safety.
        """
        discrepancy = abs(internal_balance - broker_balance)

        # We allow a tiny tolerance for expected network/rounding latency,
        # but anything beyond that triggers a total system halt.
        tolerance = max(1.0, broker_balance * 0.0001)

        if discrepancy > tolerance:
            error_msg = (f"STATE DRIFT DETECTED: Internal ${internal_balance:.2f} "
                         f"vs Broker ${broker_balance:.2f}. Discrepancy: ${discrepancy:.2f}")

            self.logger.critical(error_msg)
            # Instantly invoke the hard halt from the Governor
            self.governor.trigger_circuit_breaker(error_msg)
            return False

        return True
