import ctypes
from core.security_core import SecurityVault

def test_vault_rigor():
    vault = SecurityVault()
    secret_text = b"SUPER_SECRET_KEY_123"

    # 1. Add secret to vault
    buffer = vault.add_secret('api_key', secret_text)
    address = ctypes.addressof(buffer)

    print(f"Secret stored at address: {hex(address)}")

    # 2. Verify it is there
    assert buffer.value == secret_text
    print("Verification: Secret exists in memory.")

    # 3. Shred the vault
    vault.clear()

    # 4. Final Audit: Directly inspect the raw memory at the address
    # We create a view of the memory at the exact location
    mem_check = (ctypes.c_char * len(secret_text)).from_address(address)

    # SUCCESS CONDITION: All bytes must be \x00
    is_zeroed = all(b == 0 for b in mem_check)

    if is_zeroed:
        print("SUCCESS: Memory has been successfully sanitized.")
    else:
        # If it hits this, your memset failed to clear the memory
        print(f"FAILURE: Data still persists: {bytes(mem_check)}")

if __name__ == "__main__":
    test_vault_rigor()
