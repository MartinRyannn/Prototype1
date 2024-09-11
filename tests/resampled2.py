import pandas as pd
import tpqoa
from datetime import datetime

class ConTrader(tpqoa.tpqoa):
    def __init__(self, config_file, instrument, bar_length):
        super().__init__(config_file)
        self.instrument = instrument
        self.bar_length = pd.to_timedelta(bar_length)
        self.tick_data = pd.DataFrame()
        self.last_bar = pd.Timestamp(datetime.utcnow(), tz="UTC")

    def on_success(self, time, bid, ask):
        print(self.ticks, end=" ")

        recent_tick = pd.to_datetime(time).tz_convert("UTC")
        df = pd.DataFrame({self.instrument: (ask + bid) / 2},
                          index=[recent_tick])
        self.tick_data = pd.concat([self.tick_data, df])

        if recent_tick - self.last_bar >= self.bar_length:
            self.resample_and_join()

    def resample_and_join(self):
        self.data = self.tick_data.resample(self.bar_length, label="right").ohlc().ffill().iloc[:-1]
        if not self.data.empty:
            self.last_bar = self.data.index[-1]

trader = ConTrader("oanda.cfg", "XAU_USD", "1T")

trader.stream_data("XAU_USD", stop=120)

print("\nResampled Data (OHLC):")
print(trader.data)
