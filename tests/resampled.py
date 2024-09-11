import pandas as pd
import tpqoa

class GetTickData(tpqoa.tpqoa):
    def __init__(self, config_file):
        super().__init__(config_file)
        self.tick_data = pd.DataFrame()

    def on_success(self, time, bid, ask):
        print(time, bid, ask)
        df = pd.DataFrame({"bid": bid, "ask": ask, "mid": (ask + bid) / 2}, 
                          index=[pd.to_datetime(time)])
        self.tick_data = pd.concat([self.tick_data, df])


td = GetTickData("oanda.cfg")
td.stream_data("XAU_USD", stop=200)


#resampled_data = td.tick_data.resample("1T", label="right").last()
resampled_data = td.tick_data['mid'].resample('1T').ohlc()

print(resampled_data)
