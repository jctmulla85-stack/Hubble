from governance.governor import Governor
from execution.reconciler import Reconciler

def run_integration_test():
    print("--- Starting Full System Integration Test ---")

    # 1. Setup Environment
    gov = Governor(initial_equity=50000)
    rec = Reconciler(governor=gov)

    # 2. Test: Normal Operation
    # System should be healthy
    rec.verify_state(50000, 50000)
    assert gov.is_halted == False, "System halted unnecessarily!"
    print("✓ Normal state verified.")

    # 3. Test: State Drift Integration
    # If Reconciler detects drift, it MUST trip the Governor
    rec.verify_state(50000, 40000) # $10k discrepancy
    assert gov.is_halted == True, "Governor failed to halt on Reconciler drift signal!"
    print("✓ State Drift Halt: Passed")

    print("--- All Integration Tests Passed ---")

if __name__ == "__main__":
    run_integration_test()
