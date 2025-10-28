import pandas as pd
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
fmp_api_key = os.getenv('FMP_API_KEY')


ticker = "nvda.us"
end = datetime.today()
start = end - timedelta(days=1*365)

url = f"https://stooq.com/q/d/l/?s={ticker}&d1={start:%Y%m%d}&d2={end:%Y%m%d}&i=d"
nvda = (pd.read_csv(url, parse_dates=["Date"])
        .set_index("Date")
        .sort_index())

print(nvda.head(5))
print(nvda.tail(5))

# Get current market cap from FMP
ticker_symbol = "NVDA"
fmp_url = f"https://financialmodelingprep.com/api/v3/market-capitalization/{ticker_symbol}?apikey={fmp_api_key}"

response = requests.get(fmp_url)
market_cap_data = response.json()

print(market_cap_data)