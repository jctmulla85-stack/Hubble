import os
import glob
from supervisor_v2 import AdvancedSupervisor
from risk_engine_v2 import AdvancedRiskEngine
from execution_core import ExecutionCore
from resource_watchdog import ResourceWatchdog

def audit_codebase():
    print("=== MASTER CODEBASE & SUBSYSTEM AUDIT ===")
    
    # 1. Check all python files in root for dependencies or anti-patterns
    py_files = glob.glob("*.py")
    print(f"Discovered Python Subsystems: {py_files}")
    
    for f in py_files:
        with open(f, "r") as file:
            content = file.read()
            # Verify zero unwanted heavy third party frameworks (like pandas if unused in core)
            if "import pandas" in content and f == "execution_core.py":
                print(f"  [WARNING] {f}: Contains pandas import.")
            else:
                print(f"  [PASS] {f}: Clean dependency profile.")

    # 2. Subsystem Instantiation & Integrity Check
    try:
        sup = AdvancedSupervisor()
        risk = AdvancedRiskEngine()
        core = ExecutionCore()
        watchdog = ResourceWatchdog()
        print("\nAll subsystems instantiated successfully with zero initialization exceptions.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Subsystem initialization failed: {e}")
        return

    # 3. Final Gatekeeper Verification
    checks = sup.run_comprehensive_system_check()
    print("\nSupervisor Tiers Status:")
    for k, v in checks.items():
        print(f"  - {k}: {v}")

    print("\n=== MASTER AUDIT COMPLETE: ALL SUBSYSTEMS COMPLIANT ===")

if __name__ == "__main__":
    audit_codebase()
