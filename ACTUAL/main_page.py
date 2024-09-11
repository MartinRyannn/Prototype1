import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tpqoa
from datetime import datetime
import threading
import time


class MyOanda(tpqoa.tpqoa):
    def on_success(self, time, bid, ask):
        ''' Method called when new data is retrieved. '''
        try:

            timestamp = datetime.strptime(time[:23], "%Y-%m-%dT%H:%M:%S.%f")
            bid_price = float(bid)
            ask_price = float(ask)
            
            times.append(timestamp)
            bid_prices.append(bid_price)
            ask_prices.append(ask_price)
            
            if len(times) > 50:
                times.pop(0)
                bid_prices.pop(0)
                ask_prices.pop(0)
            
            update_chart()
        except Exception as e:
            print(f"Error processing tick data: {e}")

root = tk.Tk()
root.configure(bg="#040404")
root.attributes('-fullscreen', False)

plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(8, 4))

ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('')

ax.xaxis.set_visible(False)
ax.yaxis.set_visible(False)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

times = []
bid_prices = []
ask_prices = []


def update_chart():
    ax.clear()
    
    ax.plot(times, bid_prices, 'g-', marker='o', label='Bid Price') 
    ax.plot(times, ask_prices, 'r-', marker='o', label='Ask Price')
    
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    
    ax.legend()
    canvas.draw()

def start_streaming():
    my_oanda = MyOanda("oanda.cfg")
    while True:
        my_oanda.stream_data(instrument='XAU_USD', stop=10)
        time.sleep(0.0001) 

threading.Thread(target=start_streaming, daemon=True).start()


root.mainloop()
