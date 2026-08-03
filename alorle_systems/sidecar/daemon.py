import asyncio
from sidecar.ipc_server import IPCServer
from sidecar.state_manager import StateJournal
from sidecar.engine import ConstraintMeshEngine

class ConstraintMeshDaemon:
    def __init__(self, socket_path="/tmp/alorle.sock"):
        self.journal = StateJournal()
        self.engine = ConstraintMeshEngine(state_journal=self.journal, max_daily_drawdown_pct=0.045)
        self.ipc_server = IPCServer(socket_path=socket_path, message_handler=self.process_signal)

    async def process_signal(self, msg_type, account_id, action, volume, price):
        action_str = "BUY" if action == 1 else "SELL"
        
        # Evaluate signal through the constraint mesh engine
        is_approved = self.engine.evaluate_signal(account_id, action, volume, price)
        
        if is_approved:
            print(f"[MeshDaemon] ROUTING -> Account: {account_id} | Action: {action_str} | Vol: {volume} | Price: {price}")
            # Here is where the sidecar forwards the clean signal to the broker gateway
        else:
            print(f"[MeshDaemon] BLOCKED -> Account: {account_id} trade dropped by constraint mesh.")

    async def start(self):
        print("[MeshDaemon] Starting production constraint mesh daemon...")
        await self.ipc_server.start()

    async def stop(self):
        await self.ipc_server.stop()
        print("[MeshDaemon] Constraint mesh daemon stopped safely.")

