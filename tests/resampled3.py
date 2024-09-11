import pandas as pd
import tpqoa
from datetime import datetime, timedelta

#starts live data and every 10 seconds resamples and prints the 10 second candles

class ConTrader(tpqoa.tpqoa):
    def __init__(self, config_file, instrument, bar_length):
        super().__init__(config_file)
        self.instrument = instrument
        self.bar_length = pd.to_timedelta(bar_length)
        self.tick_data = pd.DataFrame()
        self.last_bar = pd.Timestamp(datetime.utcnow(), tz="UTC")
        self.last_print_time = datetime.utcnow()

    def on_success(self, time, bid, ask):
        recent_tick = pd.to_datetime(time).tz_convert("UTC")
        df = pd.DataFrame({self.instrument: (ask + bid) / 2},
                          index=[recent_tick])
        self.tick_data = pd.concat([self.tick_data, df])

        if datetime.utcnow() - self.last_print_time >= timedelta(seconds=10):
            self.resample_and_print()

    def resample_and_print(self):
        self.data = self.tick_data.resample('10S', label="right").ohlc().ffill().iloc[:-1]
        if not self.data.empty:
            print("\nResampled Data (10-second OHLC):")
            print(self.data.tail()) 
            self.last_print_time = datetime.utcnow()

trader = ConTrader("oanda.cfg", "XAU_USD", "10S")

trader.stream_data("XAU_USD")
