import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from telegram import Bot

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Secure Imports from internal modules
from governance.logger import log_event

# --- Master Logger Setup ---
# logger removed

# Load secrets from .env
load_dotenv()
TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

class GovernorGuard:
    """
    Enterprise Governor Guard: Evaluates asynchronous trade actions, 
    enforces safety filters, and dispatches critical alerts via Telegram.
    """
    def __init__(self) -> None:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            log_event("WARNING", "[GovernorGuard Warning] TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing from environment variables.")
            self.bot: Optional[Bot] = None
        else:
            self.bot = Bot(token=TELEGRAM_TOKEN)
            log_event("INFO", "[GovernorGuard Initialized] Telegram bot dispatch interface ready.")

    async def notify(self, message: str) -> None:
        """Asynchronously sends formatted risk alerts to the configured Telegram chat."""
        if not self.bot or not TELEGRAM_CHAT_ID:
            log_event("ERROR", f"[GovernorGuard Alert Error] Cannot send notification, Telegram client uninitialized. Message: {message}")
            return

        try:
            formatted_msg = f"⚠️ {message}"
            await self.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=formatted_msg)
            log_event("INFO", f"[Telegram Alert Dispatched Successfully] {message}")
        except Exception as e:
            log_event("CRITICAL", f"[Telegram Dispatch Critical Failure] Failed to send alert: {e}")

    def evaluate(self, action_details: Dict[str, Any]) -> str:
        """Core Governor evaluation logic to vet incoming trade payloads."""
        try:
            message_content = str(action_details.get('message', '')).lower()
            if "error" in message_content or "critical" in message_content:
                log_event("WARNING", f"[Governor VETO] Trade action flagged and blocked: {action_details}")
                return "VETO"
            
            log_event("INFO", f"[Governor APPROVE] Trade action cleared: {action_details}")
            return "APPROVE"
        except Exception as e:
            log_event("ERROR", f"[Governor Error] Exception during trade evaluation: {e}")
            return "VETO" # Fail closed for security

async def main() -> None:
    """Main execution loop for worker guard evaluations and simulation dispatch."""
    log_event("INFO", "[Worker Main] Starting GovernorGuard evaluation loop.")
    guard = GovernorGuard()

    # Example Trade Loop
    pending_trades = [
        {"action": "BUY", "message": "Standard trade"},
        {"action": "SELL", "message": "CRITICAL: Connection error"}
    ]

    for trade in pending_trades:
        decision = guard.evaluate(trade)

        if decision == "VETO":
            print(f"VETOED: {trade}")
            log_event("WARNING", f"VETOED ACTION: {trade}")
            await guard.notify(f"Trade Vetoed: {trade.get('message', 'Unknown reason')}")
        else:
            print(f"APPROVED: {trade}")
            log_event("INFO", f"APPROVED ACTION: {trade}")
            # place_order(trade) # Actual trading logic goes here

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_event("INFO", "[Worker Terminated] Process interrupted by user.")
    except Exception as e:
        log_event("CRITICAL", f"[Worker Critical Crash] Unhandled exception in main event loop: {e}")

