import asyncio
from researcher import Researcher
from execution import Engine
from governance import Governor

async def research_task(res, queue):
    """The sensory organ: constantly watching the market."""
    while True:
        data = res.fetch_latest_bars("SPY")
        await queue.put(data) # Send data to the nervous system
        await asyncio.sleep(60)

async def execution_task(eng, gov, queue):
    """The motor organ: reacting to decisions."""
    while True:
        data = await queue.get() # Listen for data
        signal = "BUY" # Placeholder for advanced algorithm
        if gov.validate_signal(signal):
            eng.place_market_order("SPY", 1, "buy")
        queue.task_done()

async def main():
    res, eng, gov = Researcher(), Engine(), Governor()
    queue = asyncio.Queue()

    # Run the organs in parallel
    await asyncio.gather(
        research_task(res, queue),
        execution_task(eng, gov, queue)
    )

if __name__ == "__main__":
    asyncio.run(main())
