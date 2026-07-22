import os
import sys
import ctypes
import logging
from typing import Dict, Any, Optional

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

class SecurityVault:
    """
    Enterprise SecurityVault: Manages sensitive secrets in low-level mutable memory buffers 
    using ctypes and provides direct RAM zeroization capabilities.
    """
    def __init__(self) -> None:
        self._vault: Dict[str, ctypes.Array[ctypes.c_char]] = {}
        logger.info("[SecurityVault Initialized] Secure memory vault ready.")

    def add_secret(self, key_id: str, secret_bytes: bytes) -> Optional[ctypes.Array[ctypes.c_char]]:
        """Stores secret bytes in a mutable, C-compatible memory buffer."""
        try:
            if not isinstance(key_id, str) or not isinstance(secret_bytes, bytes):
                logger.error("[SecurityVault Error] Invalid types provided for secret insertion.")
                return None
            
            buffer = ctypes.create_string_buffer(secret_bytes)
            self._vault[key_id] = buffer
            logger.info(f"[SecurityVault Secret Stored] Key ID '{key_id}' successfully secured in memory buffer.")
            return buffer
        except Exception as e:
            logger.critical(f"[SecurityVault Critical] Failed to allocate secret for '{key_id}': {e}")
            return None

    def _zeroize(self, buffer: ctypes.Array[ctypes.c_char]) -> None:
        """Writes zeros directly to the RAM address, bypassing Python's garbage collection."""
        try:
            address = ctypes.addressof(buffer)
            size = ctypes.sizeof(buffer)
            ctypes.memset(address, 0, size)
            logger.debug(f"[SecurityVault Zeroize] Memory block at address {address} (size: {size} bytes) zeroed out.")
        except Exception as e:
            logger.critical(f"[SecurityVault Critical] Memory zeroization failed: {e}")

    def clear(self) -> None:
        """Clears all stored secrets by securely zeroing out their RAM blocks."""
        try:
            for key_id in list(self._vault.keys()):
                self._zeroize(self._vault[key_id])
                del self._vault[key_id]
            logger.info("[SecurityVault Cleared] All vault memory blocks successfully zeroized and purged.")
            print("Vault cleared: Memory zeroed.")
        except Exception as e:
            logger.critical(f"[SecurityVault Critical] Error during vault clearance: {e}")

    def restart_from_hard_stop(self, fingerprint_verified: bool) -> bool:
        """
        Restarts the system from a hard stop shutdown state upon successful 
        mobile biometric fingerprint verification.
        """
        try:
            if fingerprint_verified:
                logger.info("[Hardware Security] Biometric fingerprint validated. Initiating system restart from hard stop shutdown.")
                print("System restarting from hard stop state...")
                return True
            else:
                logger.warning("[Hardware Security Warning] Fingerprint verification failed. Hard stop state maintained.")
                return False
        except Exception as e:
            logger.critical(f"[Hardware Security Critical] Exception during hard-stop restart sequence: {e}")
            return False

if __name__ == "__main__":
    vault = SecurityVault()
    test_buffer = vault.add_secret("api_key", b"super_secret_trading_token")
    
    # Test fingerprint hardware restart hook from hard stop
    restart_status = vault.restart_from_hard_stop(fingerprint_verified=True)
    print(f"System Hard-Stop Restart Status: {restart_status}")
    
    vault.clear()

