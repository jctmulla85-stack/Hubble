import time
import sys

class ExecutionProfiler:
    def __init__(self, max_latency_ms=50.0):
        self.max_latency_ms = max_latency_ms

    def measure_execution(self, func, *args, **kwargs):
        """
        Measures execution time of a trading loop or order router function 
        to ensure deterministic speed across large symbol baskets.
        """
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        print(f"[LATENCY PROFILER] Execution Time: {elapsed_ms:.2f}ms (Threshold: {self.max_latency_ms}ms)")
        
        if elapsed_ms > self.max_latency_ms:
            print(f"[WARNING] Execution bottleneck detected! Latency exceeded limit by {(elapsed_ms - self.max_latency_ms):.2f}ms")
            return result, "SLOW_EXECUTION"

        return result, "OPTIMAL"
