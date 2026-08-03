import asyncio
import struct

PACKET_FORMAT = "!B Q B d d"

class SidecarClient:
    def __init__(self, socket_path="/tmp/alorle.sock"):
        self.socket_path = socket_path

    async def send_order(self, msg_type: int, account_id: int, action: int, volume: float, price: float):
        payload = struct.pack(PACKET_FORMAT, msg_type, account_id, action, volume, price)
        reader, writer = await asyncio.open_unix_connection(self.socket_path)
        try:
            writer.write(payload)
            await writer.drain()
        finally:
            writer.close()
            await writer.wait_closed()
