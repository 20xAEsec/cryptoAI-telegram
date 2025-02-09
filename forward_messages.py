import nest_asyncio
nest_asyncio.apply()  # Allow nested event loops (useful in VS Code)

import asyncio
from telethon import TelegramClient, events
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
import json
import coin_info
load_dotenv()

# --- TELEGRAM AND OPENAI CONFIGURATION ---

# Replace with your own credentials from my.telegram.org
api_id = int(os.getenv("APP_API_ID"))          # e.g., 1234567 (as an integer)
api_hash = os.getenv("APP_API_HASH")             # e.g., 'abcdef1234567890abcdef1234567890'
session_name = 'user_session'                    # Session file name

# Configure the source and target chats:
# Pass numeric IDs as integers.
#source_chat = int(os.getenv("ALGORA_BOT_USERID"))  # The source chat's numeric ID
source_chat = int(os.getenv("MY_USER_ID"))  # The source chat's numeric ID
target_chat = int(os.getenv("CHAT_ID"))            # The target group chat's numeric ID


gpt_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
)
# Create the Telegram client (logs in as a user)
client = TelegramClient(session_name, api_id, api_hash)

async def call_chatgpt(prompt: str) -> str:
    """
    Asynchronously calls ChatGPT using the new OpenAI API interface.
    Returns ChatGPT's response text.

    """

    token_info = coin_info.get_token_info(prompt)
    #print(str(token_info))
    if token_info:
        compact_token_info = json.dumps(token_info, separators=(',', ':'))
        # write the token info to a file in a format that is easy to read with indentation
        with open("token_info.json", "w") as outfile:
            json.dump(token_info, outfile, indent=4)
        print("TOKEN FOUND - CoinGecko data in prompt")
        full_prompt = (
            "This is a message from a Telegram bot that calls out specific meme coins that are about to pop off.\n"
            "Use the content to provide an in-depth analysis of the meme coin being called out, performing your own research of the trading metrics.\n"
            "Generate a response that is informative and technical to the users in the group chat.\n"
            "Structure your response in a visually easy-to-read format that provides value.\n"
            "Keep your response concise and to the point, avoiding unnecessary fluff.\n"
            "Message below:\n" + prompt +
            "\nIn addition, provide an in-depth analysis of the provided data on this token, and provide a prediction on the token's future price movement, and wether this is a good investment currently.\n"        
            "I will provide the coin info in Base64 format. Decode the data and use the resulting information for your analysis\n"
            "Coin info from CoinGecko API: + \n" + str(compact_token_info)
        )
    else:
        full_prompt = (
            "This is a message from a Telegram bot that calls out specific meme coins that are about to pop off.\n"
            "Use the content to provide an in-depth analysis of the meme coin being called out, performing your own research of the trading metrics.\n"
            "Generate a response that is informative and engaging to the users in the group chat.\n"
            "Structure your response in a visually easy-to-read format that provides value.\n"
            "Keep your response concise and to the point, avoiding unnecessary fluff.\n"
            "Message below:\n" + prompt
        )

    #print(str(full_prompt))
    chat_completion = gpt_client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": full_prompt,
        }
    ],
    model="gpt-3.5-turbo",
)
    # Return the assistant's reply
    return chat_completion.choices[0].message.content

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
        chatgpt_response = await call_chatgpt(message_text)

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
