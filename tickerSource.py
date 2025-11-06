import pandas as pd
from datetime import datetime, timedelta
import os

# IF YOU TRY TO RUN THIS FILE, AND GET NO OUTPUT
# YOU HAVE TO SET build_new_formatted_list = True

# Stores a mapping between a stock's (ticker, country_code) and its "/path/from/local/dir"
# Also works with stonk to help direct calls to either the API or the local databases.


relative_folderpath = "data/stooq/"
raw_datapath = "data/stooq/filepaths.txt"
formatted_datapath = "data/stooq/filepathsformatted.txt"
# ^^ Could improve my format with a "verbose Country" column that says, like, "United States" instead of "us"
# and maybe even detects international stocks
# although honestly, it should be a higher-level overhead to this -- that should be a function in 
# TickerSource, not an entire column in the data.




# set this flag to "True" if you want to run the file (python3 tickerSource.py) and re-build
# the filepathsformatted.txt file from the filepaths.txt file
build_new_formatted_list = False

# I learned about class-level attributes in Python to build this part
# I knew I only wanted to make this dataframe once in the whole program's execution, but I wasn't sure
# how exactly to do that with Python. This is good OOP.
# the "Class-Level Attribute" feature is essentially a way to ensure that this large dataframe is shared 
# across all instances, instead of every object storing its own 25kb mapping.
# (wouldn't be the end of the world on modern machines, but let's be intentional here.)
class TickerSource:
    df = None

    def __init__(self):
        if TickerSource.df is None:
            print("Loading tickerSource dataframe")
            TickerSource.df = pd.read_csv(formatted_datapath)
        
        self.df = TickerSource.df

    def numStocksLoaded(self):
        valueCounts = self.df["COUNTRY"].value_counts()
        print(f"num stocks loaded for each country:\n{valueCounts}")

    # ensures there's no duplicate ticker symbols
    def checkTickers(self):
        valueCounts = self.df["TICKER"].value_counts()
        # print(f"Type: {type(valueCounts)}")
        print(valueCounts)
        count_of_counts = valueCounts.value_counts()
        print(f"Count of counts: {count_of_counts}")

        # Count of counts: 1    22326
        #                  2     1014
        #                  3       27
        #                  4        3

        # So yeah, there are 2.2k unique tickers,
        # but about 1k with duplicates
        # 27 with triplets
        # and 3 with quadruples.
        # This deal is a sure thing. I now own triples of the barracuda.

    def getPath(self, ticker, country, printout=False):
        try:
            # my og code was foolish I guess
            # slice = self.df["COUNTRY" == country]["TICKER" == ticker]
            # filepath = slice["FILEPATH"].iloc[0]
            # slice = self.df[(self.df["COUNTRY"] == country) & (self.df["TICKER"] == ticker)]
            slice = self.df[(self.df["COUNTRY"] == country) & (self.df["TICKER"] == ticker)]
            topSlice = slice["FILEPATH"].iloc[0]

            # Be sure to include the relative_folderpath in here
            filepath = f"{relative_folderpath}{topSlice}" 

            if printout: 
                print(f"filepath for {ticker}.{country} == {filepath}")

            return filepath
        except Exception as e:
            print(f"[Warning] ticker not found for {ticker}.{country}", end='\t')
            print(f" -- because of error {e}")
            return "FAILED/PATH"
        
    # Tests if os can actually find the file from getPath
    def testPath(self, ticker, country):
        testResult = self.getPath(ticker, country)
        if os.path.exists(testResult):
            print(f"FOUND {ticker}.{country} \t at {testResult}")
            return True
        else:
            print(f"NOT FOUND {ticker}.{country} \t at {testResult}")
            return False







# How did I build this?
# 1. Navigate in terminal to the data folder
# 2. Run "find . > filepaths.txt" to create a text document with all of the directory names
# 3. Programmatically manipulate that file line-by-line to create an associative document "filepathsformatted.txt" 
# 4. Read this formatted list with pandas


# (more verbose description):
# For this part, I went into my stooq folder
# and I ran a "find ." in terminal
# Then I took the output, and I copied it,
# and pasted it into filepaths.txt in the data folder.
# I then used this function to build it into a pandas-friendly .txt file
# That way, I could store mappings.

# COUNTRY,EXCHANGE,TICKER,FILEPATH
# filepaths.txt is at "data/stooq/filepaths.txt"



# gets the filepath of this ticker's daytrade info, stored locally 
def getLocalPath(ticker):
    print(f"nice try, {ticker}")
    
# Creates the formatted list from the raw list
def formatFromRaw(fullService=True):
    # if fullService = True, write the entire list, not just testing a portion

    row_count = 0
    if os.path.exists(raw_datapath):
        print(f"found raw data at {raw_datapath}")
        with open(raw_datapath, "r") as f:
            row_count = sum(1 for _ in f)
            print(f"Number of rows: {row_count}")
    else:
        print(f"could not find raw data at {raw_datapath}")

    df_raw = pd.read_csv(raw_datapath, sep="\n")
    print("Printing first 10 raw entries:")
    print(df_raw.head(10))

    # Split the filepath by '/' and expand into separate columns
    # split_cols = df_raw[0].split("/")
    # print(f"split_cols: \n{split_cols}")

    # TICKER,COUNTRY,EXCHANGE,FILEPATH
    df_formatted = pd.DataFrame(columns=["COUNTRY", "EXCHANGE", "TICKER", "FILEPATH"])
    
    #
    # # Ok, it looks like:

    # iloc goes from 3 to 24535
    # skip lines that don't end in ".txt"

    # 1. country is in split("/")[1]
    # 2. exchange is in split("/")[2]
    # 3. "ticker.code.txt" is in split("/")[len - 1]
    # 4. "path" is FROM THE STOOQ FOLDER, so be sure to append relative_folderpath when accessing

    # iloc goes from 3 to 24535 for the full range
    endIndex = 100
    if fullService:
        endIndex = row_count # write the full output

    linesToWrite = []
    linesToWrite.append("TICKER,COUNTRY,EXCHANGE,FILEPATH\n")
    print(linesToWrite)
    for i in range(3, endIndex):
        try:
            row = df_raw.iloc[i][0]
            splitdata = row.split("/")
            if splitdata[-1].split(".")[-1] != "txt":
                print(f"no ticker at {row}")
            else:
                # print(f"splitdata, iloc at {i} = {splitdata}")
                country = splitdata[1]
                exchange = splitdata[2]
                ticker = splitdata[-1].split(".")[0]
                path = row[2:]

                newline=f"{ticker},{country},{exchange},{path}\n"
                print(newline, end='')
                linesToWrite.append(newline)
                # print(f"successfully parsed {row}")

        except Exception as e:
            print(f"exception at {i}, {e}")


    # Now, to write the final file.
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(formatted_datapath), exist_ok=True)  # only if you have subfolders

        # Open in write mode (overwrites existing file)
        with open(formatted_datapath, "w") as f:
            for line in linesToWrite:
                f.write(line)

    except Exception as e:
            print(f"exception: {e}")


    if fullService:
        print("Done running formatFromRaw() with full service")
    else:
        print("Done testing formatFromRaw()")

        

# TICKER,COUNTRY,EXCHANGE,FILEPATH
if build_new_formatted_list:
    formatFromRaw()

