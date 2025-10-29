import pandas as pd
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from EODHDHandler import EODHDHandler



# What am I trying to do here?
# We want to see what industries each nation is investing in, over the past 30 years.
# So we have to build out a list of symbols. For each nation, we'll have its top 100 stocks. 
#       For each stock, we can name its industry, when it was born, and when it died (or how it's going today)
#       Then, we can build a report for each of those symbols showing quarterly movements (high, low, close, etc).
#       So, we'll have a json file for every single symbol's high-level data (like what nation it's in, what its industries are, etc)
#       And then we'll build out a bunch of json files for every symbol where we make the below calls and aggregate the data
#       I sort of want total quarterly money movement in and out of each company.
# So, for a list of countries, we should take each one's top 100 stocks each year.
# Then, with all of those stocks, 

# one stock for one year is 52kb.
# 1. Make a list of symbols to track
# 2. For each symbol, 

# 2024-11-01  134.691  137.301  134.561  135.361  207142109


# Nah bro, okay, here's what to do.
# 1. Encapsulate the API access
# 2. Find a way to store tables about total + average money moves for a specific symbol over a specific time period.


'''
{
        "date": "2024-10-29",
        "open": 140.285,
        "high": 142.2598,
        "low": 138.9,
        "close": 141.25,
        "adjusted_close": 141.2095,
        "volume": 157593594
      },


            Open    High       Low   Close     Volume
Date                                                    
2025-10-22  181.140  183.44  176.7600  180.28  162249552
2025-10-23  180.420  183.03  179.7901  182.16  111363718
2025-10-24  183.835  187.47  183.5000  186.26  131296677
2025-10-27  189.990  192.00  188.4318  191.49  153452704
2025-10-28  193.050  203.15  191.9100  201.03  295866116
'''



# Load environment variables from .env file
load_dotenv()


ticker = "nvda.us"
end = datetime.today()
start = end - timedelta(days=1*365)


url = f"https://stooq.com/q/d/l/?s={ticker}&d1={start:%Y%m%d}&d2={end:%Y%m%d}&i=d"
nvda = (pd.read_csv(url, parse_dates=["Date"])
        .set_index("Date")
        .sort_index())

print(nvda.head(5))
print(nvda.tail(5))

