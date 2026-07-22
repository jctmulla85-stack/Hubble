import os
import sys
import socket
import logging
from typing import Optional

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from governance.logger import get_master_logger

# --- Master Logger Setup ---
logger = get_master_logger()

class ConnectivityWatchdog:
    """
    Enterprise ConnectivityWatchdog Module: Continuously monitors network health,
    broker endpoint availability, and operational environment modes.
    """
    def __init__(self, host: str = "api.alpaca.markets", port: int = 443, timeout: float = 5.0) -> None:
        self.host: str = host
        self.port: int = port
        self.timeout: float = float(timeout)
        self.mode: str = os.getenv("BOT_MODE", "MOCK").upper()
        logger.info(f"[Watchdog Initialized] Mode: {self.mode} | Target: {self.host}:{self.port}")

    def is_connected(self) -> bool:
        """Evaluates network and broker reachability based on active operational mode."""
        try:
            if self.mode == "MOCK":
                logger.info("[Watchdog] MOCK MODE ACTIVE - Connection check bypassed successfully.")
                return True

            # Production Live/Paper Socket Reachability Check
            socket.setdefaulttimeout(self.timeout)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                logger.debug(f"[Watchdog] Successfully established socket connection to {self.host}:{self.port}")
                return True

        except socket.timeout:
            logger.warning(f"[Watchdog Warning] Connection timeout reached while pinging {self.host}:{self.port}")
            return False
        except socket.error as se:
            logger.error(f"[Watchdog Error] Socket connection failed to {self.host}:{self.port}: {se}")
            return False
        except Exception as e:
            logger.critical(f"[Watchdog Critical] Unhandled exception during connectivity check: {e}")
            return False

if __name__ == "__main__":
    watchdog = ConnectivityWatchdog()
    status = watchdog.is_connected()
    print(f"Connectivity Status: {status}")

