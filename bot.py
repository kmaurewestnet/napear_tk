from telegram import Bot
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

def bot_message(message):
    TOKEN = os.getenv ("TOKEN")
    CHAT_ID = os.getenv ("CHAT_ID")

    bot = Bot(token=TOKEN)

    asyncio.run(bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown"))
