from sidecar.vault import LocalVault

# Initialize vault
vault = LocalVault()

# Dummy master passphrase for your local VPS environment
passphrase = "alorle_secure_master_key_2026"

# Sample API keys
dummy_keys = {
    "account_id": 998877,
    "api_key": "alpaca_live_key_xyz123",
    "api_secret": "alpaca_secret_key_abc789"
}

# Store encrypted
vault.store_credentials(passphrase, dummy_keys)

# Load and verify decryption
loaded_keys = vault.load_credentials(passphrase)
print("[Vault] Successfully retrieved decrypted credentials:", loaded_keys)
