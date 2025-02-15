import nest_asyncio
nest_asyncio.apply()  # Allow nested event loops (useful in VS Code)

from telethon import TelegramClient, events
from openai import OpenAI
from gpt_actions import gpt_client, call_chatgpt, extract_token_name_and_platform, gpt_cryptoanalysis
import os

# Replace with your own credentials from my.telegram.org
api_id = int(os.getenv("APP_API_ID"))          # e.g., 1234567 (as an integer)
api_hash = os.getenv("APP_API_HASH")             # e.g., 'abcdef1234567890abcdef1234567890'
session_name = 'user_session'                    # Session file name

# Configure the source and target chats:
# Pass numeric IDs as integers.
#source_chat = int(os.getenv("ALGORA_BOT_USERID"))  # The source chat's numeric ID
source_chat = int(os.getenv("MY_USER_ID"))  # The source chat's numeric ID
target_chat = int(os.getenv("CHAT_ID"))            # The target group chat's numeric ID



# gpt_client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
# )
# Create the Telegram client (logs in as a user)
client = TelegramClient(session_name, api_id, api_hash)


@client.on(events.NewMessage(chats=source_chat))


async def handler(event):
    """
    When a new message arrives from the source chat:
      1. It calls ChatGPT to get a response based on the message.
      2. Forwards the original message to the target chat.
      3. Sends ChatGPT's response to the target chat.
    """
    try:
        message_text = event.message.message
        if not message_text:
            print("No text found in the message; skipping.")
            return

        # Get ChatGPT's response asynchronously
        #chatgpt_response = await gpt_cryptoanalysis(message_text)
        chatgpt_response = await gpt_cryptoanalysis(message_text)

        # Forward the original message to the target group
        await client.forward_messages(entity=target_chat, messages=event.message)
        print(f"Forwarded message {event.message.id} from {source_chat} to {target_chat}")

        # Send ChatGPT's response to the target group
        await client.send_message(entity=target_chat, message=chatgpt_response)
        print("Sent ChatGPT response to the target chat.")

    except Exception as e:
        print(f"Error in handler: {e}")



async def main():
    """Starts the client and keeps it running until disconnected."""
    print("Client is running. Press Ctrl+C to stop.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.start()  # Logs in and creates session if needed
    client.loop.run_until_complete(main())
