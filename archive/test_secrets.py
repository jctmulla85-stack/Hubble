import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

# Load the .env file
load_dotenv()

async def test_telegram():
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("ERROR: Secrets not found. Check your .env file!")
        return

    print("Success: Secrets loaded.")
    bot = Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text="🚀 System Test: Governor integration is online.")
        print("Success: Telegram message sent.")
    except Exception as e:
        print(f"ERROR: Failed to send message: {e}")

if __name__ == "__main__":
    asyncio.run(test_telegram())
