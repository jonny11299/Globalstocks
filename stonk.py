import pandas as pd
from datetime import datetime, timedelta
import os



# Time to encapsulate some stock knowledge
# This Stonk is a single stock. It only has one symbol. 
class Stonk:
    def __init__(self, symb = "NVDA", country = "US"):
        # Stores the name of the stock. The Stooq library uses country codes like "NVDA.US" in the function call.
        self.symb = f"{symb}.{country}"
        # Creates a blank dataframe for keeping stock data
        self.day_df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])               
        self.month_df = pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])           
    

    def print(self):
        print(f"Printing daily trades for stock {self.symb}")
        print(self.day_df)
        print("----------------------")
        print(f"Printing monthly trades for stock {self.symb}")
        print(self.month_df)



    # Flag sort as "true" if you want to sort it
    def _append_day_df(self, dfin, sort=True):
        try:
            self.day_df = pd.concat([self.day_df, dfin], ignore_index=True)
            if sort:
                self.day_df = self.day_df.sort_values(by="Date", ascending=True).reset_index(drop=True)
        except Exception as e:
            print(f"Failed to append dataframe, {e}")


    # Flag sort as "true" if you want to sort it
    def _append_month_df(self, dfin, sort=True):
        try:
            self.month_df = pd.concat([self.month_df, dfin], ignore_index=True)
            if sort:
                self.month_df = self.month_df.sort_values(by="Date", ascending=True).reset_index(drop=True)
        except Exception as e:
            print(f"Failed to append dataframe, {e}")


    # Returns the dataframe (row) of a single day's activity
    # columns=["Date", "Open", "High", "Low", "Close", "Volume"]) 
    # Append will tell this function to append the results to its own internal df,
    # thereby saving the changes. By default, we want it to be False to save
    # on memory. We can just return the results and print the results of the function
    def getDayTrade(self, day:datetime, append = False):
        # verify day is valid. Returns an empty dataframe if not.
        if day > datetime.today():
            print(f"[Warning] trying to getDayTrade in the future: {day:%Y-%m-%d}")
            return pd.DataFrame()

        try:
            url = f"https://stooq.com/q/d/l/?s={self.symb}&d1={day:%Y%m%d}&d2={day:%Y%m%d}&i=d"

            df = (pd.read_csv(url, parse_dates=["Date"])
                    .sort_values("Date"))
            
            if append: self._append_day_df(df, False) # don't sort

            return df
            
        except Exception as e:
            print(f"[Warning] Failed to fetch {self.symb} for {day:%Y-%m-%d} from url: {url}:\nerror: {e}")
            return pd.DataFrame()  # return an empty frame instead of None
        

    # Returns a dataframe of daily trade activity for this symbol   
    def getDayTradeRange(self, day1:datetime, day2:datetime, append = False):
        # verify day is valid. Returns an empty dataframe if not.
        if day1 > datetime.today() or day2 > datetime.today():
            print(f"[Warning] trying to getDayTradeRange in the future: day1 = {day1:%Y-%m-%d}, day2 = {day2:%Y-%m-%d}")
            return pd.DataFrame()

        try:
            url = f"https://stooq.com/q/d/l/?s={self.symb}&d1={day1:%Y%m%d}&d2={day2:%Y%m%d}&i=d"

            df = (pd.read_csv(url, parse_dates=["Date"])
                    .sort_values("Date"))
            
            if append: self._append_day_df(df, False) # don't sort
            
            return df
            
        except Exception as e:
            print(f"[Warning] Failed to fetch {self.symb} for {day:%Y-%m-%d} from url: {url}:\nerror: {e}")
            return pd.DataFrame()  # return an empty frame instead of None
        
    # Returns a dataframe of monthly trade activity for this symbol
    def getMonthTradeRange(self, day1:datetime, day2:datetime, append = False):
        if day1 > datetime.today() or day2 > datetime.today():
            print(f"[Warning] trying to getMonthTradeRange in the future: day1 = {day1:%Y-%m-%d}, day2 = {day2:%Y-%m-%d}")
            return pd.DataFrame()

        try:
            url = f"https://stooq.com/q/d/l/?s={self.symb}&d1={day1:%Y%m%d}&d2={day2:%Y%m%d}&i=m"

            df = (pd.read_csv(url, parse_dates=["Date"])
                    .sort_values("Date"))
            
            if append: self._append_month_df(df, False) # don't sort
            
            return df
            
        except Exception as e:
            print(f"[Warning] Failed to fetch {self.symb} for {day:%Y-%m-%d} from url: {url}:\nerror: {e}")
            return pd.DataFrame()  # return an empty frame instead of None