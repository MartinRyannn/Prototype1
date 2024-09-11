import pandas as pd
import tpqoa
from datetime import datetime, timedelta

api = tpqoa.tpqoa("oanda.cfg")

yesterday = datetime.now() - timedelta(1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

data = api.get_history(instrument="XAU_USD", start=yesterday_str, end=(yesterday + timedelta(1)).strftime('%Y-%m-%d'), granularity="D", price="B")
#data2 = api.get_history(instrument="XAU_USD", start="2024-09-09", end="2024-09-09", granularity="D", price="B")

if not data.empty:
    open_price = data["o"].iloc[0]
    high = data["h"].iloc[0]
    low = data["l"].iloc[0]
    close = data["c"].iloc[0]
    
    print(f"open: {open_price:.2f}, high: {high:.2f}, low: {low:.2f}, close: {close:.2f}")
    
    # Pivot Point = (Previous High + Previous Low + Previous Close) / 3
    pivot_point = (high + low + close) / 3
    # Support 1 (S1) = (Pivot Point * 2) - Previous High
    s1 = (pivot_point * 2) - high
    # Support 2 (S2) = Pivot Point - (Previous High - Previous Low)
    s2 = pivot_point - (high - low)
    # Resistance 1 (R1) = (Pivot Point * 2) - Previous Low
    r1 = (pivot_point * 2) - low
    # Resistance 2 (R2) = Pivot Point + (Previous High - Previous Low)
    r2 = pivot_point + (high - low)
    
    print(f"pivot point: {pivot_point:.2f}, s1: {s1:.2f}, s2: {s2:.2f}, r1: {r1:.2f}, r2: {r2:.2f}")
else:
    print("No data found for the specified date.")
