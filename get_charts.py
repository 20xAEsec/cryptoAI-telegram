import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from string import Template


import requests

def get_tradingview_symbol(query, exchange='BINANCE', asset_type='crypto', lang='en'):
    """
    Query TradingView's symbol search endpoint to get symbol details for a crypto token.

    Parameters:
        query (str): The search term (e.g., "PEPE", "BTC").
        exchange (str): The exchange to filter by (default is 'BINANCE').
        asset_type (str): The asset type (default is 'crypto').
        lang (str): The language for the results (default is 'en').

    Returns:
        dict or None: The first matching symbol's details as a dictionary, or None if no match is found.
    """
    url = "https://symbol-search.tradingview.com/symbol_search/"
    params = {
        'text': query,
        'exchange': exchange,
        'lang': lang,
        'type': asset_type,
    }
    # It can help to set a common browser User-Agent header.
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raises HTTPError if the request returned an unsuccessful status code.
        results = response.json()
        
        if results:
            # Return the first match (or modify this logic to select the best match)
            return results[0]
        else:
            print("No matching symbols found for query:", query)
            return None

    except requests.RequestException as e:
        print("An error occurred during the request:", e)
        return None






# -----------------------------------------------------------------------------
# 1. Create an HTML file that embeds TradingView widgets for the PEPE token.
# 2. Saves the 1 day, 1 week, and 1 month charts as .png files in local directory, and local variables
# Returns the local variables for the charts (TradingView Containers)
# -----------------------------------------------------------------------------

def generate_charts(exchange, symbol):

    html_content = Template("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <title>PEPE TradingView Charts</title>
    <!-- Load TradingView's widget library -->
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    </head>
    <body>
    <!-- Container for 1-Day Chart -->
    <div id="tradingview_chart_day" style="height: 400px; margin-bottom: 20px;"></div>
    <!-- Container for 1-Week Chart -->
    <div id="tradingview_chart_week" style="height: 400px; margin-bottom: 20px;"></div>
    <!-- Container for 1-Month Chart -->
    <div id="tradingview_chart_month" style="height: 400px; margin-bottom: 20px;"></div>
    
    <script type="text/javascript">
        // 1-Day (Daily) Chart Widget
        new TradingView.widget({
        "width": "100%",
        "height": 400,
        "symbol": "$exchange:$symbol",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "container_id": "tradingview_chart_day"
        });
        
        // 1-Week (Weekly) Chart Widget
        new TradingView.widget({
        "width": "100%",
        "height": 400,
        "symbol": "$exchange:$symbol",
        "interval": "W",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "container_id": "tradingview_chart_week"
        });
        
        // 1-Month (Monthly) Chart Widget
        new TradingView.widget({
        "width": "100%",
        "height": 400,
        "symbol": "$exchange:$symbol",
        "interval": "M",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "container_id": "tradingview_chart_month"
        });
    </script>
    </body>
    </html>
    """).substitute(exchange=exchange, symbol=symbol)

    # Write the HTML content to a local file.
    html_file = f"tradingview_{symbol}.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # -----------------------------------------------------------------------------
    # 2. Set up Selenium to open the HTML file in a headless Chrome browser.
    # -----------------------------------------------------------------------------
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")            # Run Chrome in headless mode.
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Use webdriver-manager to automatically handle the ChromeDriver binary.
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Construct the file URL for the HTML file.
    file_url = "file://" + os.path.abspath(html_file)
    driver.get(file_url)

    # -----------------------------------------------------------------------------
    # 3. Wait for the TradingView widgets to load.
    #    (Adjust the sleep duration if necessary.)
    # -----------------------------------------------------------------------------
    print("Waiting for charts to render...")
    time.sleep(20)  # Waiting 20 seconds for the widgets to fully load.

    # -----------------------------------------------------------------------------
    # 4. Locate each chart container and take a screenshot.
    # -----------------------------------------------------------------------------
    try:
        # Find the container elements by their IDs.
        day_chart = driver.find_element(By.ID, "tradingview_chart_day")
        week_chart = driver.find_element(By.ID, "tradingview_chart_week")
        month_chart = driver.find_element(By.ID, "tradingview_chart_month")
        
        # Capture screenshots of each chart container.
        day_chart.screenshot(f"./charts/{symbol}_chart_1day.png")
        week_chart.screenshot(f"./charts/{symbol}_chart_1week.png")
        month_chart.screenshot(f"./charts/{symbol}_chart_1month.png")
        
        print("Screenshots saved as:")
        print(f" - ./charts/{symbol}_chart_1day.png")
        print(f" - ./charts/{symbol}_chart_1week.png")
        print(f" - ./charts/{symbol}_chart_1month.png")

        return day_chart, week_chart, month_chart
    except Exception as e:
        print("An error occurred while taking screenshots:", e)
    finally:
        # Close the browser.
        driver.quit()

def main():
    exchange = 'CRYPTO'
    symbol = 'XCN'
    result = generate_charts(exchange,f"{symbol}USD")

main()