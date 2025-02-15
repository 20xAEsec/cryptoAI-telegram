import re
import requests
import json

def get_token_info(text: str):
    """
    Given an input string that may contain a crypto token contract address,
    this function will:
      1. Scan the string for a contract address matching one of several blockchain formats:
           - EVM-compatible (e.g., Ethereum, BSC):    \b0x[a-fA-F0-9]{40}\b
           - Pumpfun tokens:                           \bPF[a-fA-F0-9]{40}\b
           - Tezos:                                    \bKT1[1-9A-HJ-NP-Za-km-z]{33}\b
           - Tron:                                     \bT[1-9A-HJ-NP-Za-km-z]{33}\b
           - Cardano:                                  \b(?:addr1|addr_test1)[0-9a-z]{38,}\b
           - Polkadot/Substrate:                       \b[1-9A-HJ-NP-Za-km-z]{47,48}\b
           - Solana:                                   \b[1-9A-HJ-NP-Za-km-z]{32,44}\b
      2. Identify the blockchain platform based on the matched regex.
      3. Use a mapping to convert that platform to the corresponding CoinGecko API platform identifier.
      4. Query the CoinGecko API for token information via:
         https://api.coingecko.com/api/v3/coins/<platform>/contract/<contract_address>
         
    If successful, returns the token data in JSON format.
    Otherwise, returns an error dictionary.
    """
    # Dictionary of regex patterns for each blockchain's contract address format.
    patterns = {
        "ethereum": r'\b0x[a-fA-F0-9]{40}\b',             # EVM-compatible tokens
        "pump-fun":  r'\b[A-Za-z0-9]+pump\b',              # Pumpfun tokens (assumed format)
        "tezos":    r'\bKT1[1-9A-HJ-NP-Za-km-z]{33}\b',     # Tezos
        "tron":     r'\bT[1-9A-HJ-NP-Za-km-z]{33}\b',        # Tron
        "cardano":  r'\b(?:addr1|addr_test1)[0-9a-z]{38,}\b',  # Cardano
        "polkadot": r'\b[1-9A-HJ-NP-Za-km-z]{47,48}\b',       # Polkadot/Substrate
        "solana":   r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'         # Solana
    }
    data = None
    detected_platform = None
    contract_address = None
    
    # Scan the input text for a matching contract address.
    for platform, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            contract_address = match.group(0)
            detected_platform = platform
            print(str(f'Contract address detected: {contract_address} (platform: {detected_platform})'))
            break
    
    if not contract_address:
        print(f"========\nerror - No valid contract address found in the input text.\n Input Text - {text}\n========")
        return None
    
    # Map the detected platform to CoinGecko's expected platform identifier.
    platform_mapping = {
        "ethereum": "ethereum",
        "pump-fun": "pump-fun",    # Support for Pumpfun tokens
        "tezos": "tezos",
        "tron": "tron",
        "cardano": "cardano",
        "polkadot": "polkadot",
        "solana": "solana"
    }
    
    if detected_platform not in platform_mapping:
        print("PLATFORM NOT SUPPORTED")
        return None
    
    coingecko_platform = platform_mapping[detected_platform]
    
    # Construct the CoinGecko API URL.
    base_url = "https://api.coingecko.com/api/v3/coins"
    api_url = f"{base_url}/{coingecko_platform}/contract/{contract_address}"
    
    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            print( "error - Token not found or API error")
            return None
        data = response.json()
        return data
    except Exception as e:
        print( {"error": str(e)})
        return None

def get_contract_address(token_name: str, blockchain: str) -> str:
    """
    Given a token's name and a blockchain (e.g., "ethereum", "binance-smart-chain"),
    queries the CoinGecko API and returns the token's contract address.

    Args:
        token_name (str): The name of the token to search for.
        blockchain (str): The blockchain for which to retrieve the contract address.
    
    Returns:
        str: The contract address if found, otherwise None.
    """
    # Step 1: Search for the token using the CoinGecko search endpoint.
    search_url = "https://api.coingecko.com/api/v3/search"
    params = {"query": token_name}
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        print(f"Error: Search API request failed with status code {response.status_code}")
        return None

    search_data = response.json()
    coins = search_data.get("coins", [])
    if not coins:
        print(f"No coins found for token name: {token_name}")
        return None

    # Attempt to find an exact match by name (case-insensitive), or use the first result.
    coin_id = None
    for coin in coins:
        if coin.get("name", "").lower() == token_name.lower():
            coin_id = coin.get("id")
            break
    if coin_id is None:
        coin_id = coins[0].get("id")
    
    # Step 2: Retrieve detailed coin information to access the platforms data.
    details_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    # Limit data to only what we need to reduce payload.
    details_params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "false",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false"
    }
    details_response = requests.get(details_url, params=details_params)
    if details_response.status_code != 200:
        print(f"Error: Details API request failed with status code {details_response.status_code}")
        return None

    details_data = details_response.json()
    platforms = details_data.get("platforms", {})

    # Step 3: Extract the contract address for the specified blockchain.
    # The blockchain keys are typically in lowercase.
    contract_address = platforms.get(blockchain.lower())
    if not contract_address:
        print(f"No contract address found for blockchain: {blockchain}")
        return None

    return contract_address

# token_name = "LOFI"
# blockchain = "SUI"
# address = get_contract_address(token_name, blockchain)
# if address:
#     print(f"Contract address for {token_name} on {blockchain}: {address}")
# else:
#     print("Contract address not found.")