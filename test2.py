import pandas as pd
from datetime import datetime, timedelta
import os
from stonk import Stonk
from tickerSource import TickerSource






print("--------------------------------------- NEW RUN OF test2.py ----------------------------------")




# Returns a timestamp from 'd' days ago
def daysago(d: int):
    return datetime.today() - timedelta(days=(d))

def datetimeTesting():
    print(datetime.today())
    today = datetime.today()
    lastyear = today - timedelta(days=365)
    print(f"Today: {today:%Y%m%d}")

    y2k = datetime(2000, 1, 1)
    print(f"y2k: {y2k}")
    distance = datetime.today()-y2k
    print(f"Time since y2k: {distance}")

   

def getFunctionTesting():
    nvda = Stonk()
    # print(f"days=1{nvda.getDayTrade(datetime.today() - timedelta(days=1))}")
    # print(f"days=3{nvda.getDayTrade(datetime.today() + timedelta(days=3))}")
    # print(f"days=101{nvda.getDayTrade(datetime.today() - timedelta(days=101))}")
    # print(f"days=981{nvda.getDayTrade(datetime.today() - timedelta(days=981))}")
    # print(f"days=9000{nvda.getDayTrade(datetime.today() - timedelta(days=9000))}")
    # print(f"days=6{nvda.getDayTrade(datetime.today() - timedelta(days=6))}")
    # print("\n\n\nGonna print myself fr this time: ")
    # nvda.print()
    print(f"testing day trade with 2000-01-01: \n{nvda.getDayTrade(datetime(2000, 1, 1))}")
    print(f"testing day trade with 2000-01-02: \n{nvda.getDayTrade(datetime(2000, 1, 2))}")
    print(f"testing day trade with 2000-01-03: \n{nvda.getDayTrade(datetime(2000, 1, 3))}")
    print(f"testing day trade with 2000-01-04: \n{nvda.getDayTrade(datetime(2000, 1, 4))}")
    print("\n\n\n")


    print("Testing save feature:")
    stonk2 = Stonk("PRME")
    stonk2.getDayTradeRange(datetime.today() - timedelta(days=(100)), datetime.today() - timedelta(days=(80)), True)
    stonk2.getDayTradeRange(datetime.today() - timedelta(days=(50)), datetime.today() - timedelta(days=(70)), True)
    stonk2.getDayTradeRange(datetime.today() - timedelta(days=(65)), datetime.today() - timedelta(days=(85)), True)
    # stonk2.getMonthTradeRange(datetime.today() - timedelta(days=(200)), datetime.today() - timedelta(days=(50)), True)
    stonk2.print()


    print("----------------------------------------------\n\n\n\n\n\n\n")

    stonk3 = Stonk("NVDA", "US")
    stonk3.getDayTradeRange(datetime(2000, 1, 1), datetime(2000, 3, 1), True)
    stonk3.print()


    print("----------------------------------------------\n\n\n\n\n\n\n")

    print("Testing monthly data features:")
    stonk4 = Stonk("airi", "us")
    stonk4.getMonthTradeRange(datetime.today() - timedelta(days=(400)), datetime.today() - timedelta(days=(80)), True)
    stonk4.getMonthTradeRange(datetime.today() - timedelta(days=(500)), datetime.today() - timedelta(days=(300)), True)
    stonk4.getMonthTradeRange(datetime.today() - timedelta(days=(1200)), datetime.today() - timedelta(days=(85)), True)
    # stonk2.getMonthTradeRange(datetime.today() - timedelta(days=(200)), datetime.today() - timedelta(days=(50)), True)
    stonk4.print()

    print()
    print()


def readingFromFilesTesting():
    # First, we get a hold of the syntax for reading dfs from files
    path = "data/stooq/uk/lse stocks/alph.uk.txt"
    df = pd.read_csv(path)
    print(f"Printing at {path}")
    print(df.head(10))
    df.columns = df.columns.str.strip("<>").str.upper()

    print(f"Printing at {path} post-strip")
    print(df.head(10))

    # Formatting correctly
    df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d")
    for col in ["OPEN", "HIGH", "LOW", "CLOSE", "VOL", "OPENINT"]:
        df[col] = pd.to_numeric(df[col])


    # Now we call the actual class method
    print("Reading zoo.uk.txt")
    stock2 = Stonk("ZOO", "UK")
    stock2.print()


    # The below requires matplotlib
    # I'll need to figure out how to export it.
    # df["HIGH"].plot(title="alph.uk.txt HIGH")


    #  Date      Open      High       Low     Close     Volume adjustedVolume
    # -->
    # TICKER PER      DATE  TIME    OPEN    HIGH     LOW   CLOSE     VOL  OPENINT

    # switch to upper
    # add TICKER, PER

def nextTradingDayTest():
    nvda = Stonk("NVDA", "US")
    startDate = datetime(2015, 1, 1)
    print("Gonna output a lot here \n")
    for i in range(0, 18):
        day2 = startDate + timedelta(days=i)
        print(f"next trading day from {day2}:")
        nvda.nextTradingDay(day2)



def tickerSourceTesting():
    src = TickerSource()
    src.numStocksLoaded()
    # src.checkTickers()

    # get 10 random tickers, see if we can find their filepath
    print("------- Testing filepath access with random tickers ---------")
    print("----- Head: -----")
    randomTickers = TickerSource.df.sample(n=100)
    print(randomTickers.head(30))
    print(type(randomTickers))

    print("----- OS Test: -----")
    # Learned about "iter tuples" and "iterrows()" I guess.
    for row in randomTickers.itertuples(index=False):
        ticker = row.TICKER
        country = row.COUNTRY
        testResult = src.testPath(ticker, country)



def smarterFunctionsTesting():
    date1 = datetime.today() - timedelta(days=101)
    date2 = datetime.today() - timedelta(days=101 + 1*365)
    date3 = datetime.today() - timedelta(days=50 + 4*365)
    date4 = datetime.today() - timedelta(days=20 + 5*365)
    date5 = datetime.today() - timedelta(days=40)

    # test if we are storing our saved date ranges correctly
    st = Stonk("NVDA", "US")
    st.getDayTradeRange(date1, date2, True)
    st.inRange(date1 + timedelta(days=5), date1 + timedelta(days=10))
    st.inRange(date1 - timedelta(days=5), date1 + timedelta(days=10))
    st.inRange(date1 - timedelta(days=5), date1 - timedelta(days=10))
    st.getDayTradeRange(date3, date4, True)
    st.inRange(date3 + timedelta(days=5), date3 + timedelta(days=10))
    st.inRange(date3 - timedelta(days=5), date3 + timedelta(days=10))
    st.inRange(date3 - timedelta(days=5), date3 - timedelta(days=10))
    st.getDayTradeRange(date4, date5, True)
    st.inRange(date4 + timedelta(days=5), date4 + timedelta(days=10))
    st.inRange(date4 - timedelta(days=5), date5 + timedelta(days=10))
    st.inRange(date4 - timedelta(days=5), date5 - timedelta(days=10))




# tickerSourceTesting()
getFunctionTesting()
# readingFromFilesTesting()
# smarterFunctionsTesting()

# Alright, sick, I did it. I built a way to access the local files.
# Now, I need to use this filepath to create a Stonk object
# And I need to modify the Stonk object to intelligently use local access before global access.
# Maybe it'll test dates first, then try local access, and if failed, resort to API access
# I should wrap an API call in a function that always knows when it makes an API call though, and prints it out.
# That should be a fairly big alert.
# like "APIString, Reason" so that you have to say why you're doing it.
    




'''
From GPT: 

✅ Correct ways to iterate rows
Option 1: iterrows() (most common)
for idx, row in randomTickers.iterrows():
    ticker = row["TICKER"]
    country = row["COUNTRY"]
    path = src.getPath(ticker, country, True)
    print(ticker, country, path)


row is a Series representing a single row.

idx is the row index.

Works perfectly for accessing column values.

Option 2: itertuples() (faster, more memory-efficient)
for row in randomTickers.itertuples(index=False):
    ticker = row.TICKER
    country = row.COUNTRY
    path = src.getPath(ticker, country, True)
    print(ticker, country, path)


row is a namedtuple, so you can access columns as attributes.

Faster than iterrows() if performance matters.

Option 3: Vectorized (avoid explicit loop)
paths = [
    src.getPath(ticker, country, True)
    for ticker, country in zip(randomTickers["TICKER"], randomTickers["COUNTRY"])
]


Pure Python list comprehension.

Often the cleanest if you don’t need the row index.
'''