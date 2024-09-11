import pandas as pd
import tpqoa
from datetime import datetime, timedelta

api = tpqoa.tpqoa('oanda.cfg')


hist_data = api.get_history(instrument='XAU_USD', start='2024-08-26', end='2024-08-30', granularity='D', price='M')
hist_data = hist_data.reset_index()
hist_data.to_csv("historical.csv")

for index, row in hist_data.iterrows():
    start_date = pd.to_datetime(row['time'])
    end_date = start_date + timedelta(days=1)

    start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

    minute_data = api.get_history(instrument='XAU_USD', start=start_str, end=end_str,  granularity='M15', price='M')

    file_name = f"15min_data_{start_date.strftime('%Y-%m-%d')}.csv"
    minute_data.to_csv(file_name)
    
    print(f"15-minute data for {start_str[:10]} saved to {file_name}")

print(hist_data)