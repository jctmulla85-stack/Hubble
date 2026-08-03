import asyncio
from sidecar.daemon import ConstraintMeshDaemon
from alorle_systems.core.bot import CoreBotClient
from sidecar.state_manager import StateJournal

async def run_integration():
    # 1. Initialize state for testing
    journal = StateJournal()
    account_id = 998877
    journal.update_account_state(account_id, current_equity=50000.0, locked=0)

    # 2. Start the daemon
    daemon = ConstraintMeshDaemon()
    await daemon.start()
    await asyncio.sleep(0.1) # Allow socket bind

    # 3. Fire a test signal via the core bot client over Unix socket
    client = CoreBotClient()
    print("\n[Integration] Firing live test packet through Unix socket...")
    await client.dispatch_signal(account_id=account_id, action=1, volume=1.0, price=65000.0)

    await asyncio.sleep(0.3)

    # 4. Shut down daemon cleanly
    await daemon.stop()

if __name__ == "__main__":
    asyncio.run(run_integration())
