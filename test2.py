import pandas as pd
from datetime import datetime, timedelta
import os
from stonk import Stonk

print(datetime.today())
today = datetime.today()
lastyear = today - timedelta(days=365)
print(f"Today: {today:%Y%m%d}")


y2k = datetime(2000, 1, 1)
print(f"y2k: {y2k}")
distance = datetime.today()-y2k
print(f"Time since y2k: {distance}")


'''
nvda = Stonk()
print(f"days=1{nvda.getDayTrade(datetime.today() - timedelta(days=1))}")
print(f"days=3{nvda.getDayTrade(datetime.today() + timedelta(days=3))}")
print(f"days=101{nvda.getDayTrade(datetime.today() - timedelta(days=101))}")
print(f"days=981{nvda.getDayTrade(datetime.today() - timedelta(days=981))}")
print(f"days=9000{nvda.getDayTrade(datetime.today() - timedelta(days=9000))}")
print(f"days=6{nvda.getDayTrade(datetime.today() - timedelta(days=6))}")
print("\n\n\nGonna print myself fr this time: ")
nvda.print()
print("\n\n\n")
'''

print("Testing save feature:")
stonk2 = Stonk("PRME")
stonk2.getDayTradeRange(datetime.today() - timedelta(days=(100)), datetime.today() - timedelta(days=(50)), True)
stonk2.getMonthTradeRange(datetime.today() - timedelta(days=(100)), datetime.today() - timedelta(days=(50)), True)
stonk2.print()


print("----------------------------------------------\n\n\n\n\n\n\n")