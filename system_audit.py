import os
from supervisor_v2 import AdvancedSupervisor
from risk_engine_v2 import AdvancedRiskEngine
from execution_core import ExecutionCore

def audit_all_modules():
    print("=== BEGINNING FULL SYSTEM AUDIT: APEX_001 ===")
    
    # 1. Audit Supervisor & Multi-Tier Guards
    supervisor = AdvancedSupervisor()
    sup_results = supervisor.run_comprehensive_system_check()
    print("\n[1] Supervisor & Risk Tiers:")
    for k, v in sup_results.items():
        print(f"    - {k}: {v}")
        
    # 2. Audit Risk Engine
    risk_engine = AdvancedRiskEngine()
    risk_results = risk_engine.evaluate_execution_integrity()
    print(f"\n[2] Advanced Risk Engine: {risk_results}")
    
    # 3. Audit Execution Core Initialization
    try:
        core = ExecutionCore()
        print(f"\n[3] Execution Core: INITIALIZED (Paper Mode: {core.paper})")
    except Exception as e:
        print(f"\n[3] Execution Core: ERROR -> {e}")

    print("\n=== FULL SYSTEM AUDIT COMPLETE ===")

if __name__ == "__main__":
    audit_all_modules()
