import asyncio
from alorle_systems.sidecar.ipc_server import IPCServer

async def main():
    server = IPCServer()
    if os.path.exists(server.socket_path):
        os.remove(server.socket_path)
    
    server.server = await asyncio.start_unix_server(
        server.handle_connection, path=server.socket_path
    )
    os.chmod(server.socket_path, 0o600)
    print(f"[IPC] Sidecar listening on secure Unix socket: {server.socket_path}")
    async with server.server:
        await server.server.serve_forever()

if __name__ == "__main__":
    import os
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
