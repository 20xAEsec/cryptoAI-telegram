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
    
    system_prompt = """"
    You are an expert cryptocurrency trader and technical analyst. "
        "You have comprehensive knowledge of on-chain metrics, volume, price data, "
        "and market trends. Your task is to analyze the provided token data, "
        "assess metrics such as trading volume, liquidity, price trends, and risk factors, "
        "and then provide a detailed technical analysis along with a recommendation "
        "on whether the token is a good buy.
        """
    #print(str(token_info))
    if token_info:
        
        token_name = token_info["name"]
        token_platform = token_info["asset_platform_platform"]
        print(print("TOKEN DATA FOUND AND RETRIEVED - CoinGecko data in prompt"))
        token_info["market_data"]["current_price"] = token_info["market_data"]["current_price"]["usd"]
        token_info["market_data"]["ath"] = token_info["market_data"]["ath"]["usd"]
        token_info["market_data"]["ath_date"] = token_info["market_data"]["ath_date"]["usd"]
        token_info["market_data"]["atl"] = token_info["market_data"]["atl"]["usd"]
        token_info["description"] = token_info["description"]["en"]
        token_info["localization"] = token_info["localization"]["en"]
        token_info["market_data"]["ath_change_percentage"] = token_info["market_data"]["ath_change_percentage"]["usd"]
        token_info["market_data"]["high_24h"] = token_info["market_data"]["high_24h"]["usd"]
        token_info["market_data"]["low_24h"] = token_info["market_data"]["low_24h"]["usd"]
        token_info["tickers"] = token_info["tickers"][0:5]

        # write the token info to a file in a format that is easy to read with indentation
        with open("token_info.json", "w") as outfile:
            json.dump(token_info, outfile, indent=4)
            

        full_prompt = (
            """You are an expert financial analyst specializing in cryptocurrency markets. You are receiving calls in a Telegram channel on crypto tokens that need to be analyzed. 
              The contract address is extracted from the message to query the CoinGecko API and provide you with the results on the token data.
              Please perform a highly detailed and in-depth analysis of the  using the data provided. Only consider the data points pertaining to the price and market data of the token in your analysis.

            Your analysis should include:

            1. **Summary of Key Metrics:**  
            - Identify and list the most important metrics from the JSON token data(e.g., current price, volume, market cap, technical indicators, trend signals, etc.).
            - Explain briefly what each metric means in the context of crypto token performance.

            2. **Detailed Analysis:**  
            - For each key metric, discuss its current value, historical context (if provided), and what it might indicate about the token’s performance.
            - Analyze any patterns or anomalies. For example, if there is a significant change in volume or price, discuss potential causes and implications.
            - Evaluate the token's technical signals (such as support/resistance levels, trend lines, moving averages, RSI, MACD, etc.) and explain how they contribute to your overall conclusion.

            3. **Comparative Insights and Conclusion:**  
            - Based on the metrics, provide an overall assessment of the token’s current state and potential future performance.
            - Explain your reasoning step-by-step, showing how the data supports the conclusion you reach.
            - Include any potential risks or red flags indicated by the data.
            - Conclude with a summary statement that clearly outlines your overall findings.

            4. **Transparency in Reasoning:**  
            - Ensure that your analysis is comprehensive and shows exactly how each data point influenced your conclusion.
            - Use clear, technical language suitable for an audience familiar with crypto markets, while ensuring that each point is well-explained.

            Do not reflect the data used in your analysis in your response. Here is the JSON token data:

            {token_info}

            "Here is the Telegram message that calls out the token to be analyzed:\n" + {prompt} +
        """
        )
    else:
        print("Sending prompt without CoinGecko data")
        full_prompt = (
            """You are an expert financial analyst specializing in cryptocurrency markets. Please perform a highly detailed and in-depth analysis of this token using the data provided. 

            Your analysis should include:

            1. **Summary of Key Metrics:**  
            - Explain briefly what each metric means in the context of crypto token performance.

            2. **Detailed Analysis:**  
            - For each key metric, discuss its current value, historical context (if provided), and what it might indicate about the token’s performance.
            - Analyze any patterns or anomalies. For example, if there is a significant change in volume or price, discuss potential causes and implications.
            - Evaluate the token's technical signals (such as support/resistance levels, trend lines, moving averages, RSI, MACD, etc.) and explain how they contribute to your overall conclusion.

            3. **Comparative Insights and Conclusion:**  
            - Based on the metrics, provide an overall assessment of the token’s current state and potential future performance.
            - Explain your reasoning step-by-step, showing how the data supports the conclusion you reach.
            - Include any potential risks or red flags indicated by the data.
            - Conclude with a summary statement that clearly outlines your overall findings.

            4. **Transparency in Reasoning:**  
            - Ensure that your analysis is comprehensive and shows exactly how each data point influenced your conclusion.
            - Use clear, technical language suitable for an audience familiar with crypto markets, while ensuring that each point is well-explained.
            "Message below:\n" + {prompt}
        """
        )


    chat_completion = gpt_client.chat.completions.create(
    messages=[
         {
            "role": "user",
            "content": system_prompt,
        },
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
