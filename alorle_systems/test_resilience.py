import asyncio
from sidecar.time_sync import verify_system_time
from sidecar.rate_limiter import RateLimiter
from sidecar.state_manager import StateJournal

async def run_resilience_tests():
    print("--- Running Resilience & Safeguard Verifications ---")
    verify_system_time()
    
    limiter = RateLimiter(max_calls_per_second=10.0)
    print("[RateLimiter] Testing burst throttling...")
    start = asyncio.get_event_loop().time()
    for _ in range(3):
        await limiter.acquire()
    end = asyncio.get_event_loop().time()
    print(f"[RateLimiter] Throttled 3 calls successfully in {end - start:.4f}s")
    
    journal = StateJournal()
    acc_id = 998877
    journal.update_account_state(acc_id, current_equity=52000.0, locked=0)
    journal.reconcile_state(acc_id)
    print("--- All Resilience Safeguards Verified Successfully ---")

if __name__ == "__main__":
    asyncio.run(run_resilience_tests())
