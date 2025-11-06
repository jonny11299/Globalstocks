import pandas as pd
from datetime import datetime, timedelta
import os
from tickerSource import TickerSource

# Set to "True" for testing flags / printouts, otherwise "False"
TEST = True


# Time to encapsulate some stock knowledge
# This Stonk is a single stock. It only has one symbol. 

# To make this from a local file, make sure you strip the "TICKER" symbol because it doesn't need to be copied across the entire column
class Stonk:
    def __init__(self, symb = "NVDA", country = "US"):
        # Stores the name of the stock. The Stooq library uses country codes like "NVDA.US" in the function call.
        self.symb = f"{symb}.{country}"
        # Creates a blank dataframe for keeping stock data
        self.day_df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "adjustedVolume"])               
        self.month_df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume", "adjustedVolume"])
        self.day_df.columns = self.day_df.columns.str.upper()
        self.month_df.columns = self.day_df.columns.str.upper()
        self.day_df["PER"] = "D"
        self.month_df["PER"] = "M"



    # Init from a filepath:
    # To do this, for example, type the following: 
    # stock = Stonk.from_txt("data/stooq/uk/lse stocks/alph.uk.txt")
    @classmethod
    def fromfile(cls, filepath):
        try:
            df = pd.read_csv(filepath)
            print(f"Constructing from file {filepath}")
            # print(df.head(10))
            df.columns = df.columns.str.strip("<>").str.upper()
            print(f"Printing at {filepath} post-strip")
            print(df.head(10))

            # Formatting correctly
            df["DATE"] = pd.to_datetime(df["DATE"], format="%Y%m%d")
            for col in ["OPEN", "HIGH", "LOW", "CLOSE", "VOL", "OPENINT"]:
                df[col] = pd.to_numeric(df[col])

            if df.size > 0:
                # Constructing object now:
                ticker = df.iloc[0]["TICKER"]
                print("Ticker:")
                print(ticker)
                print(f"Type: {type(ticker)}")
                symbol, countryCode = ticker.split(".") 
                stonk = cls(symb=symbol, country=countryCode)

                # may result in weird behavior where, if the condition is invalid somehow, then
                # all of the data just gets shoved into stonk.month_df, even though it's not 
                per = df.iloc[0]["PER"]
                if per == "D":
                    stonk.day_df = df
                elif per == "M":
                    stonk.month_df = df
                else:
                    print(f"[Warning] stock data at {filepath} is not defind as Daily nor Monthly. Dumping {ticker}")
                    failedstonk = cls(symb="FAIL", country="US")
                    return failedstonk  

                return stonk
            
            else:
                print(f"[Warning] stock data is empty at {filepath}")

        except Exception as e:
            print(f"Failed to open from file, {e}")
            # weird failure behavior but it returns a new stock, "FAIL.US"
            failedstonk = cls(symb="FAIL", country="US")
            return failedstonk

    

    def print(self):
        print(f"Printing daily trades for stock {self.symb}")
        print(self.day_df)
        print("----------------------")
        print(f"Printing monthly trades for stock {self.symb}")
        print(self.month_df)



    ### Saving data:

    def _sort_day_df(self):
        self.day_df = self.day_df.sort_values(by="Date", ascending=True).reset_index(drop=True)

    def _sort_month_df(self):
        self.month_df = self.month_df.sort_values(by="Date", ascending=True).reset_index(drop=True)

    # Flag sort as "true" if you want to sort it
    def _append_day_df(self, dfin, sort=True):
        try:
            self.day_df = pd.concat([self.day_df, dfin], ignore_index=True)
            if sort:
                self._sort_day_df()
        except Exception as e:
            print(f"Failed to append dataframe, {e}")


    # Flag sort as "true" if you want to sort it
    def _append_month_df(self, dfin, sort=True):
        try:
            self.month_df = pd.concat([self.month_df, dfin], ignore_index=True)
            if sort:
                self._sort_month_df()
        except Exception as e:
            print(f"Failed to append dataframe, {e}")


    # Stock market is not always open.
    # This function gets the next trading day available for (stock)
    # it basically casts a range from that day, forwards one week, and picks the earliest one available.
    # Limitation: Only works for past dates
    # Will break if a stock holiday exceeds 1 week.
    def nextTradingDay(self, day:datetime):
        df = self.getDayTradeRange(day, day + timedelta(days=7), False)
        if df == pd.DataFrame():
            # Expands the search to 3 weeks in case a stock holiday exceeds 1 week
            df = self.getDayTradeRange(day, day + timedelta(days=21), False)
        date = df.iloc[0]["DATE"]
        date = date.to_pydatetime()
        if TEST:
            print(f"nextTradingDay date type: {type(date)}")
            print(f"nextTradingDay date: {date}")
            print("-------")
            print(f"Entire df: {df}")
        return date




    ### Getting data:
    ### Todo: 
        # Creating a lookup table for stocks
        # Default to using Local Data, else, look online.
        # Will have to save a field here:
            # Last updated (when the downloaded data ends)
            # Range [(day1, day2), (day1, day2), (day1, day2), etc...]
            # The above function tells which aspects of the stock are saved in local memory, for 
            # immediate pandas access.

            # Will have to maybe consider day equivalencies with "nextTradingDay" function...
        
        # Figure out my queryTrailingStockPercent function.

        # Honestly any 

        # Eventually it'll be cool to have a list of every single symbol available,
        # its countries, its sectors, its obv,
        # from there I can calculate each year whether that stock traded up or down,
        # and how much $$$ financially.
        # Then you can see what stocks were rising and falling, what sectors, etc

        # Eventually build a cute front-facing application with like, 
        # a user interface and graphs and stuff.


    # Returns the dataframe (row) of a single day's activity
    # columns=["Date", "Open", "High", "Low", "Close", "Volume"]) 
    # Save will tell this function to append the results to its own internal df,
    # thereby saving the changes. By default, we want it to be False to save
    # on memory. We can just return the results and print the results of the function
    def getDayTrade(self, day:datetime, save = False) -> pd.DataFrame:
        # verify day is valid. Returns an empty dataframe if not.
        if day > datetime.today():
            print(f"[Warning] trying to getDayTrade in the future: {day:%Y-%m-%d}")
            # Return an empty dataframe on this failed behavior:
            return pd.DataFrame()

        try:
            url = f"https://stooq.com/q/d/l/?s={self.symb}&d1={day:%Y%m%d}&d2={day:%Y%m%d}&i=d"

            df = (pd.read_csv(url, parse_dates=["Date"])
                    .sort_values("Date"))
            
            # switch to upper
            # add PER
            df.columns = df.columns.str.upper()
            df["PER"] = "D"
            
            if save: self._append_day_df(df, False) # don't sort by default

            return df
            
        except Exception as e:
            print(f"[Warning] Failed to fetch {self.symb} for {day:%Y-%m-%d} from url: {url}:\nerror: {e}")
            return pd.DataFrame()  # return an empty frame instead of None
        

    # Returns a dataframe of daily trade activity for this symbol   
    def getDayTradeRange(self, day1:datetime, day2:datetime, save = False) -> pd.DataFrame:
        if day1 > day2: # swap the values to ensure day1 is less than day2
            day1, day2 = day2, day1 
        # verify day is valid. Returns an empty dataframe if not.
        if day1 > datetime.today() or day2 > datetime.today():
            print(f"[Warning] trying to getDayTradeRange in the future: day1 = {day1:%Y-%m-%d}, day2 = {day2:%Y-%m-%d}")

            if day1 > datetime.today():
                # Return an empty dataframe on this failed behavior. Both dates are in the future.
                return pd.DataFrame()
            if day2 > datetime.today():
                # day1 is in the past, so just return for (day1: today)
                day2 = datetime.today()

        try:
            url = f"https://stooq.com/q/d/l/?s={self.symb}&d1={day1:%Y%m%d}&d2={day2:%Y%m%d}&i=d"

            df = (pd.read_csv(url, parse_dates=["Date"])
                    .sort_values("Date"))
            df.reset_index(drop=True)

            # switch to upper
            # add PER
            df.columns = df.columns.str.upper()
            df["PER"] = "D"
            
            if save: self._append_day_df(df, False) # don't sort by default
            
            return df
            
        except Exception as e:
            print(f"[Warning] Failed to fetch {self.symb} for {day:%Y-%m-%d} from url: {url}:\nerror: {e}")
            return pd.DataFrame()  # return an empty frame instead of None
        
    # Returns a dataframe of monthly trade activity for this symbol
    def getMonthTradeRange(self, day1:datetime, day2:datetime, save = False) -> pd.DataFrame:
        if day1 > day2: # swap the values to ensure day1 is less than day2
            day1, day2 = day2, day1 
        # verify day is valid. Returns an empty dataframe if not.
        if day1 > datetime.today() or day2 > datetime.today():
            print(f"[Warning] trying to getDayTradeRange in the future: day1 = {day1:%Y-%m-%d}, day2 = {day2:%Y-%m-%d}")

            if day1 > datetime.today():
                # Return an empty dataframe on this failed behavior. Both dates are in the future.
                return pd.DataFrame()
            if day2 > datetime.today():
                # day1 is in the past, so just return for (day1: today)
                day2 = datetime.today()

        try:
            url = f"https://stooq.com/q/d/l/?s={self.symb}&d1={day1:%Y%m%d}&d2={day2:%Y%m%d}&i=m"

            df = (pd.read_csv(url, parse_dates=["Date"])
                    .sort_values("Date"))
            df.reset_index(drop=True)

            # switch to upper
            # add PER
            df.columns = df.columns.str.upper()
            df["PER"] = "M"
            
            if save: self._append_month_df(df, False) # don't sort
            
            return df
            
        except Exception as e:
            print(f"[Warning] Failed to fetch {self.symb} for {day:%Y-%m-%d} from url: {url}:\nerror: {e}")
            return pd.DataFrame()  # return an empty frame instead of None
        

    def setDayTrade(self, day:datetime):
        return self.getDayTrade(day, save=True)

    def setDayTradeRange(self, day1:datetime, day2:datetime):
        return self.getDayTradeRange(day1, day2, save=True)

    def setMonthTradeRange(self, day1:datetime, day2:datetime):
        return self.getMonthTradeRange(day1, day2, save=True)

        

    # Uses daily trade data to answer the question of:
    # If I had entered a trailing stop order on this stock
    # at x%, 
    # Sample output:
    # If you had placed a Trailing Stop order on {NVDA} for {15%} on {dayEntered},
    # then, by endDate,
        # it would have filled on {fill date} at {fill price}
        # (else, if not,) it would not have filled by endDate and would remain open.
    # initial price on (date) = 
    # max price on (date) = 
    # order executed? (yes/no)
    # fill price = (price)
    # fill date = (this day) / (n/a, order still open)
    def queryTrailingStopPercent(self, percent, startDate, endDate=datetime.today()):

        # Uses HLC/3 estimate (high + low + close)/3
        print("noth ere yet")



# Next: make it intelligent about whether it needs to load from local, or load from online.
# This will also define if we need synchronous or asynchronous behavior.
# Doesn't seem like we need any async code, yet, though. I think that's excessive.
# If we need to wait for every single stooq call sequentially, we can do that.
# Shouldn't be abusing stooq calls anyways...

# We'll need to learn logging instead of printing everything out verbose.
        

'''On-Balance Volume (OBV)
    A simple but effective indicator:
    If Close > Previous Close: OBV += Volume
    If Close < Previous Close: OBV -= Volume
    If Close = Previous Close: OBV unchanged
    Rising OBV = accumulation, Falling OBV = distribution
    '''
'''
    # Returns the overall On-Balance-Volume (OBV) using daily calculations
    def getOBVDaily(self, day1, day2) -> int:
        df = self.getDayTradeRange(day1, day2)

        if df != pd.DataFrame():
            
        else:
            print("Warning: getOBVDaily received an empty DataFrame()")
            return -1

    # Returns the overall On-Balance-Volume (OBV) using monthly calculations
    def getOBVMonthly(self) -> int:


    def getOBVListDaily(self) -> list[tuple[datetime, int]]:

    
    def getOBVListMonthly(self) -> list[tuple[datetime, int]]:
'''
'''
    ### Calculating data, making observations on data:
With just OHLCV (Open, High, Low, Close, Volume), you can estimate sentiment using several approaches:
    1. Price-Volume Relationship

    Close > Open + High Volume = Likely net buying pressure (buyers willing to pay up)
    Close < Open + High Volume = Likely net selling pressure (sellers aggressive)
    Close ≈ Open + High Volume = Indecision/churn

    2. On-Balance Volume (OBV)
    A simple but effective indicator:
    If Close > Previous Close: OBV += Volume
    If Close < Previous Close: OBV -= Volume
    If Close = Previous Close: OBV unchanged
    ```
    Rising OBV = accumulation, Falling OBV = distribution'''

#    def getOBV(self, df: pd.DataFrame, 








'''

Candlestick Anatomy
Each bar represents one trading period (in this case, one day):
The "Body" (the thick colored rectangle)

Top of body = whichever is higher: Open or Close
Bottom of body = whichever is lower: Open or Close
Green/White body = Close > Open (price went up that day)
Red/Black body = Close < Open (price went down that day)

The "Wicks" or "Shadows" (the thin lines)

Upper wick = extends from top of body to the High
Lower wick = extends from bottom of body to the Low


    Create a candlestick chart, for daily data, and monthly data.
    Daily: 
    1. 



'''