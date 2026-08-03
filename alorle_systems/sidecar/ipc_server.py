import asyncio
import os
import struct

# Binary packet format: 
# Message Type (1 byte), Account ID (8 bytes unsigned long), 
# Action (1 byte: 1=Buy, 2=Sell), Volume (8 bytes double), Price (8 bytes double)
PACKET_FORMAT = "!B Q B d d"
PACKET_SIZE = struct.calcsize(PACKET_FORMAT)

class IPCServer:
    def __init__(self, socket_path="/tmp/alorle.sock", message_handler=None):
        self.socket_path = socket_path
        self.handler = message_handler
        self.server = None

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            while True:
                data = await reader.readexactly(PACKET_SIZE)
                if not data:
                    break
                
                # Unpack binary payload instantly with zero overhead
                msg_type, account_id, action, volume, price = struct.unpack(PACKET_FORMAT, data)
                
                # Forward to the constraint mesh handler
                if self.handler:
                    await self.handler(msg_type, account_id, action, volume, price)
                    
        except asyncio.IncompleteReadError:
            pass
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            
        self.server = await asyncio.start_unix_server(
            self.handle_connection, path=self.socket_path
        )
        os.chmod(self.socket_path, 0o600) # Restrict socket access to user only
        print(f"[IPC] Sidecar listening on secure Unix socket: {self.socket_path}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
