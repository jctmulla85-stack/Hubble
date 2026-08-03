import time
import asyncio

class RateLimiter:
    def __init__(self, max_calls_per_second: float = 5.0):
        self.interval = 1.0 / max_calls_per_second
        self.last_call_time = 0.0

    async def acquire(self):
        """Asynchronously enforces a minimum delay between outgoing gateway requests."""
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.interval:
            wait_time = self.interval - elapsed
            await asyncio.sleep(wait_time)
        self.last_call_time = time.time()
