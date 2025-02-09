import nest_asyncio
nest_asyncio.apply()  # Allow nested event loops

import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext

import os
from dotenv import load_dotenv

load_dotenv()
# Retrieve tokens from environment variables for security
TELEGRAM_TOKEN = os.getenv('CALL_BOT_ID')


async def get_chat_id(update: Update, context: CallbackContext):
    """Reply with and print the chat ID."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Your Chat ID is: {chat_id}")
    print(f"Chat ID: {chat_id}")

async def main():
    """Create the bot application, add the handler, and run polling."""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, get_chat_id))
    
    print("Bot is running... Press Ctrl+C to stop.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
