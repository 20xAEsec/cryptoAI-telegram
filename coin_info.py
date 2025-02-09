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
        print("error - No valid contract address found in the input text.")
        return False
    
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
        return False
    
    coingecko_platform = platform_mapping[detected_platform]
    
    # Construct the CoinGecko API URL.
    base_url = "https://api.coingecko.com/api/v3/coins"
    api_url = f"{base_url}/{coingecko_platform}/contract/{contract_address}"
    
    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            print( "error - Token not found or API error")
            return False
        data = response.json()
        return data
    except Exception as e:
        print( {"error": str(e)})
        return False

# Example usage:
if __name__ == "__main__":
    sample_text = (
        "Here is a Pumpfun token address: PF1234567890abcdef1234567890ABCDEF12345678. "
        "This string should trigger the Pumpfun branch and query CoinGecko accordingly."
    )
    
    token_info = get_token_info(sample_text)
    print(json.dumps(token_info, indent=2))
