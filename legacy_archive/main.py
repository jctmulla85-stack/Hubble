import asyncio
from researcher import Researcher
from execution import Engine
from governance.governor import Governor
from governance.watchdog import ConnectivityWatchdog
from memory.state_manager import StateManager
from memory.telemetry import Telemetry
from memory.logger import get_master_logger

async def main():
    # Initialize the Organism's Anatomy
    res = Researcher()
    eng = Engine()
    gov = Governor()
    watchdog = ConnectivityWatchdog()
    state = StateManager()
    telemetry = Telemetry(state)
    log = get_master_logger()

    log.info("--- ORGANISM AWAKENED: All Systems Online ---")

    while True:
        # 1. SAFETY: Pre-Flight Check (The Watchdog)
        if not watchdog.is_connected():
            log.warning("Watchdog: Connection failure. System Suspended.")
            await asyncio.sleep(30)
            continue

        try:
            # 2. PERCEPTION: Analyze Market
            df = res.fetch_latest_bars("SPY")
            signal = res.analyze_signal(df)

            # 3. REFLEXES: Governance & Risk Check
            if gov.validate_signal(signal, df):

                # 4. ACTION: Inventory-Aware Execution
                if signal == "BUY":
                    eng.place_market_order("SPY", 1, "buy")
                    state.update_position("SPY", "buy", 1)
                    log.info("Action: BUY Executed")

                elif signal == "SELL":
                    # Only sell if we have a position recorded in memory
                    if state.state['positions'].get("SPY", 0) > 0:
                        eng.place_market_order("SPY", 1, "sell")
                        state.update_position("SPY", "sell", 1)
                        log.info("Action: SELL Executed")

            # 5. DIAGNOSTICS: Update Telemetry Report
            report = telemetry.generate_report()

        except Exception as e:
            log.error(f"Reflex Triggered: {e}")

        # Heartbeat: 60 seconds
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        get_master_logger().info("--- ORGANISM HIBERNATING: Graceful Shutdown ---")
