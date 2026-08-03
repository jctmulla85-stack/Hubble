import asyncio
import struct

PACKET_FORMAT = "!B Q B d d"

class CoreBotClient:
    def __init__(self, socket_path="/tmp/alorle.sock"):
        self.socket_path = socket_path

    async def dispatch_signal(self, account_id: int, action: int, volume: float, price: float):
        # Pack data into a raw C-style binary string
        payload = struct.pack(PACKET_FORMAT, 1, account_id, action, volume, price)
        
        try:
            reader, writer = await asyncio.open_unix_connection(self.socket_path)
            writer.write(payload)
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            print(f"[Bot] Failed to dispatch signal to sidecar: {e}")
