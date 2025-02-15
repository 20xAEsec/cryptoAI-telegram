import os
from openai import OpenAI
import json
import coin_info

from dotenv import load_dotenv
load_dotenv()

gpt_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
)
# Input list of prompts to provide to ChatGPT
# Return - responses to prompts, from ChatGPT
async def call_chatgpt(prompt_list: str) -> str:
    """
    Asynchronously calls ChatGPT using the new OpenAI API interface.
    Returns ChatGPT's response text.

    """
    prompt_messages = []
    for prompt in prompt_list:
        prompt_messages.append({
            "role": "user",
            "content": prompt,
        })

    chat_completion = gpt_client.chat.completions.create(messages=prompt_messages, model="gpt-3.5-turbo",)
    
    # Return the assistant's reply
    return chat_completion.choices[0].message.content

# Queries ChatGPT to perform extraction of token name and platform from the message
# Retuns token  name and platform, extracted from GPT response
async def extract_token_name_and_platform(message: str) -> tuple:
    prompt_list = []
    contract_address_retrieval_prompt = (
            """
            Analyze this message and determine there is a crypto token name and blockchain mentioned. If so, provide this information back to me in the following format:
            Token Name : <token_name_value>
            Token Platform/Blockchain : <blockchain_value>

            Insert your determination for the crypto token name in the <token_name_value> placeholder, and your determination of the token's blockchain in the <blockchain_value> placeholder. Your response should contain the two lines containing this information, and nothing else.
            Message - {message}
            """
    )
    
    prompt_list.append(contract_address_retrieval_prompt)
    
    # Call ChatGPT with the prompt
    token_info_response = call_chatgpt(prompt_list)

    # extract the token name and platform from the response
    token_name = token_info_response.split("Token Name : ")[1].split("\n")[0]
    token_platform = token_info_response.split("Token Platform : ")[1].split("\n")[0]

    print(f"Extracted token_name - {token_name}")
    print(f"Extracted token platform - {token_platform}")
    return (token_name, token_platform)

async def gpt_cryptoanalysis(message: str) -> str:
    token_info = coin_info.get_token_info(message) # looks for contract address in message
    if token_info == None:
        print(f"======\nContract Address not found, analyzing message for token name and blockchain\nmessage - {message}\n=========")
        token_name, token_platform = extract_token_name_and_platform(message)
        contract_address = coin_info.get_contract_address(token_name, token_platform)
        token_info = coin_info.get_token_info(contract_address) # looks for contract address in message
    
    prompt_list = []

    system_prompt = """"
    You are an expert cryptocurrency trader and technical analyst. "
        "You have comprehensive knowledge of on-chain metrics, volume, price data, "
        "and market trends. Your task is to analyze the provided token data, "
        "assess metrics such as trading volume, liquidity, price trends, and risk factors, "
        "and then provide a detailed technical analysis along with a recommendation "
        "on whether the token is a good buy.
        """
    
    prompt_list.append(system_prompt)

    #print(str(token_info))
    if token_info:
        
        token_name = token_info["name"]
        token_platform = token_info["asset_platform_id"]


        print("TOKEN DATA FOUND AND RETRIEVED - CoinGecko data in prompt")        
        # Get exchanges listed on, '-' seperated list
        listed_exchanges = []
        for exchange in token_info["tickers"]:
            listed_exchanges.append(exchange["market"]["name"])
        listed_exchanges = " - ".join(listed_exchanges)


        # Strip international data from JSON elements, leaving only usd/en information
        token_info["market_data"]["current_price"] = token_info["market_data"]["current_price"]
        token_info["market_data"]["ath"] = token_info["market_data"]["ath"]
        token_info["market_data"]["ath_date"] = token_info["market_data"]["ath_date"]
        token_info["market_data"]["atl"] = token_info["market_data"]["atl"]
        token_info["description"] = token_info["description"]["en"]
        token_info["localization"] = token_info["localization"]["en"]
        token_info["market_data"]["ath_change_percentage"] = token_info["market_data"]["ath_change_percentage"]
        token_info["market_data"]["high_24h"] = token_info["market_data"]["high_24h"]
        token_info["market_data"]["low_24h"] = token_info["market_data"]["low_24h"]

        # write the token info to a file in a format that is easy to read with indentation
        with open("token_info.json", "w") as outfile:
            json.dump(token_info, outfile, indent=4)
            

        full_prompt = (
            f"""You are an expert financial analyst specializing in cryptocurrency markets. You are receiving calls in a Telegram channel on crypto tokens that need to be analyzed. 
              The contract address is extracted from the message to query the CoinGecko API and provide you with the results on the token data.
              Please perform a highly detailed and in-depth analysis of the  using the data provided. Only consider the data points pertaining to the price and market data of the token in your analysis.

            Your analysis should include:

            1. **Detailed Analysis:**  
            - For each key metric, discuss its current value, historical context (if provided), and what it might indicate about the token’s performance.
            - Analyze any patterns or anomalies. For example, if there is a significant change in volume or price, discuss potential causes and implications.
            - Evaluate the token's technical signals (such as support/resistance levels, trend lines, moving averages, RSI, MACD, etc.) and explain how they contribute to your overall conclusion.

            2. **Comparative Insights and Conclusion:**  
            - Based on the metrics, provide an overall assessment of the token’s current state and potential future performance.
            - Explain your reasoning step-by-step, showing how the data supports the conclusion you reach.
            - Include any potential risks or red flags indicated by the data.
            - Conclude with a summary statement that clearly outlines your overall findings.

            3. **Transparency in Reasoning:**  
            - Ensure that your analysis is comprehensive and shows exactly how each data point influenced your conclusion.
            - Use clear, technical language suitable for an audience familiar with crypto markets, while ensuring that each point is well-explained.

            Do not reflect the data used in your analysis in your response. Here is the token data to be used in your analysis:

            Token Name : {token_name}
            Token Platform : {token_platform}
            Token Price : {token_info["market_data"]["current_price"]["usd"]}
            Token Market Cap : {token_info["market_data"]["market_cap"]["usd"]}
            Token 24h High : {token_info["market_data"]["high_24h"]["usd"]}
            Token 24h Low : {token_info["market_data"]["low_24h"]["usd"]}
            Token All Time High : {token_info["market_data"]["ath"]["usd"]}
            Token All Time High Date : {token_info["market_data"]["ath_date"]["usd"]}
            Token All Time Low : {token_info["market_data"]["atl"]["usd"]}
            Sentiment Thumbs Up Ratio : {token_info["sentiment_votes_up_percentage"]}
            Sentiment Thumbs Down Ratio : {token_info["sentiment_votes_down_percentage"]}
            Token Description : {token_info["description"]}
            Price Change Percentage in 1h : {token_info["market_data"]["price_change_percentage_1h_in_currency"]["usd"]}
            Price Change Percentage in 24h : {token_info["market_data"]["price_change_percentage_24h"]}
            Price Change Percentage in 7d : {token_info["market_data"]["price_change_percentage_7d"]}
            Price Change Percentage in 14d : {token_info["market_data"]["price_change_percentage_14d"]}
            Price Change Percentage in 30d : {token_info["market_data"]["price_change_percentage_30d"]}
            Price Change Percentage in 60d : {token_info["market_data"]["price_change_percentage_60d"]}
            Price Change Percentage in 200d : {token_info["market_data"]["price_change_percentage_200d"]}
            Price Change Percentage in 1y : {token_info["market_data"]["price_change_percentage_1y"]}
            Market Cap Rank - All Coins on Coingecko : {token_info["market_cap_rank"]}
            Market Cap Change Percentage in 24h : {token_info["market_data"]["market_cap_change_percentage_24h"]}
            Market Cap to Fully Diluted Valuation Ratio : {token_info["market_data"]["market_cap_fdv_ratio"]}
            Twitter Followers : {token_info["community_data"]["twitter_followers"]}
            Exchanges Listed : {listed_exchanges}
            "Here is the Telegram message that calls out the token to be analyzed. Use any token information in this message in your analysis as well, if available.:\n" + {message} +
        """
        )
        prompt_list.append(full_prompt)
    else:
        print("Sending prompt without CoinGecko data")
        

        full_prompt = (
            """You are an expert financial analyst specializing in cryptocurrency markets. Please perform a highly detailed and in-depth analysis of this token using the data provided. 

            Only describe your analysis where it is used to educate me on your analysis logic. Otherwise, keep your response concise, but detailed, only mentioning information regarding your analysis. Your analysis should include:

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

        prompt_list.append(full_prompt)

    crypto_analysis_response = await call_chatgpt(prompt_list)

    return crypto_analysis_response
