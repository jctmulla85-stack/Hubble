from sidecar.vault import LocalVault
from sidecar.handshake import BrokerHandshake

# 1. Load credentials from the encrypted vault
vault = LocalVault()
passphrase = "alorle_secure_master_key_2026"
creds = vault.load_credentials(passphrase)

if creds:
    print("[Test] Loaded credentials from vault. Initiating handshake...")
    
    # 2. Initialize Handshake Engine (pointing to Alpaca Paper endpoint by default)
    handshake = BrokerHandshake(
        api_key=creds.get("api_key", ""),
        api_secret=creds.get("api_secret", ""),
        base_url="https://paper-api.alpaca.markets"
    )
    
    # 3. Perform auto-discovery
    profile = handshake.connect_and_discover()
    print("[Test] Discovered Account Profile:", profile)
else:
    print("[Test] No credentials found in vault.")
