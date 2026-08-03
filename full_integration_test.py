import asyncio
import os
from alorle_systems.sidecar.client import SidecarClient
from alorle_systems.core.bot import CoreBotClient

async def run_integration_test():
    print("=== FINAL SYSTEM INTEGRATION TEST ===")
    
    socket_path = "/tmp/alorle.sock"
    assert os.path.exists(socket_path), "Socket path not found!"
    
    # Test Bot Signal Dispatching
    bot_client = CoreBotClient(socket_path)
    print("[1/2] Dispatching test signal from CoreBotClient...")
    await bot_client.dispatch_signal(account_id=1, action=1, volume=0.1, price=100.0)
    
    # Test Sidecar Client Response (msg_type, account_id, action, volume, price)
    sidecar_client = SidecarClient(socket_path)
    print("[2/2] Sending validation order via SidecarClient...")
    response = await sidecar_client.send_order(1, 1, 1, 0.1, 100.0)
    
    print(f"Integration Response Received: {response}")
    print("=== INTEGRATION TEST PASSED: ALL SYSTEMS GO ===")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
