import tpqoa

# Define a custom subclass of tpqoa.tpqoa
class MyOanda(tpqoa.tpqoa):
    def on_success(self, time, bid, ask):
        ''' Method called when new data is retrieved. '''
        # Print bid and ask prices
        print(f"BID: {bid:.5f} | ASK: {ask:.5f}")

# Initialize the custom OANDA API class with your configuration file
my_oanda = MyOanda("oanda.cfg")

# Start streaming data for a specified instrument and duration
my_oanda.stream_data(instrument='XAU_USD', stop=10)



#TRY TO ADD PERIOD TO STREAM DATA