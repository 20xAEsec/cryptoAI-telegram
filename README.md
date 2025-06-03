# Telegram Call Bot: Crypto Token Analysis

##### Note - work in progress, bugs expected.  
Working out real-time ChatGPT response streaming into Telegram message.

## Overview
This repository contains the backend code for an advanced Telegram bot that performs in-depth analysis on crypto tokens. The bot leverages technical analysis, on-chain data, and social sentiment to provide users with actionable insights into token trading opportunities—especially for meme tokens. By accepting a token contract address from various blockchain networks, the bot extracts relevant data, queries external APIs (like CoinGecko), and returns comprehensive token information.

#### Credential Setting    
Credentials are stored in the .env file, to be referenced using the dotenv Python library.  
Credentials should never be hardcoded and should be dynamically retrieved using a cloud-based secrets manager, when possible.  
For simplicity's sake, storing secrets in an environment variable will suffice, assuming the system is protected from unauthorized access.
When contributing to this codebase, ensure your local .env file has been added to .gitignore.

## Features

- **Multi-Blockchain Token Detection:**  
  The system supports a wide range of blockchain networks by using regex patterns to detect valid contract addresses. Supported formats include:
  - **EVM-Compatible Tokens:**  
    Addresses starting with `0x` (Ethereum, Binance Smart Chain, Polygon, etc.).
  - **Pumpfun Tokens:**  
    Custom tokens with addresses starting with `PF` (assumed format).
  - **Tezos Contracts:**  
    Addresses starting with `KT1` followed by 33 Base58 characters.
  - **Tron Addresses:**  
    Addresses starting with `T` followed by 33 Base58 characters.
  - **Cardano Addresses:**  
    Addresses starting with `addr1` or `addr_test1` followed by at least 38 lowercase alphanumerics.
  - **Polkadot/Substrate Addresses:**  
    Base58 addresses with a length of 47–48 characters.
  - **Solana Addresses:**  
    Base58 addresses with a length of 32–44 characters.

- **CoinGecko API Integration:**  
  After detecting the token’s blockchain, the system maps the token to the corresponding CoinGecko platform identifier and queries the CoinGecko API for detailed token data. The returned data includes:
  - Market metrics (current price, market cap, liquidity, volume)
  - Tokenomics (total and circulating supply)
  - Community data (social sentiment, community engagement)
  - Developer activity and project fundamentals

- **Robust Error Handling:**  
  The functions are designed to return clear error messages if a token isn’t found, if there’s an API error, or if the provided input doesn’t contain a valid contract address.

- **Modular & Extendable:**  
  Key functions such as `find_coin_info` and `get_token_info` are modular. This design makes it straightforward to integrate the functionality into a larger Telegram bot system and to extend support for additional blockchain platforms in the future.

## Installation

### Prerequisites
- Python 3.7 or higher
- The following Python libraries:
  - `requests` (for making HTTP requests)
  - Standard Python modules: `re`, `json`

### Setup
Clone the repository:
```bash
git clone https://github.com/20xAEsec/cryptoAI-telegram
cd cryptoAI-telegram
```
### Configuration
Sensitive credentials are retrieved via environment variables in accordance with secure programming practices.
See .env file for sample configuration

   
#### Credential Retrieval -
```python
from dotenv import load_dotenv
load_dotenv()
chat_id = os.getenv("ALGORA_BOT_USERID") 
user_id = os.getenv("MY_USER_ID")
```
