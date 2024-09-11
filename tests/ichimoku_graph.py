import webbrowser
import http.server
import socketserver
import threading
import time
import pandas as pd
import tpqoa
import json
import plotly.graph_objects as go
import tkinter as tk
from datetime import datetime, timedelta

HTML_FILE = 'ichimoku.html'
latest_data = {}

class MyOanda(tpqoa.tpqoa):
    def __init__(self, config_file):
        super().__init__(config_file)
        self.tick_data = pd.DataFrame()
        self.last_update_time = datetime.utcnow()

    def on_success(self, time, bid, ask):
        try:
            timestamp = datetime.strptime(time[:23], "%Y-%m-%dT%H:%M:%S.%f")
            bid_price = float(bid)
            ask_price = float(ask)
            
            df = pd.DataFrame({'Timestamp': [timestamp], 'Bid': [bid_price], 'Ask': [ask_price]})
            df.set_index('Timestamp', inplace=True)
            self.tick_data = pd.concat([self.tick_data, df])

            if datetime.utcnow() - self.last_update_time >= timedelta(seconds=5):
                self.last_update_time = datetime.utcnow()
                self.resample_data()
            
        except Exception as e:
            print(f"Error processing tick data: {e}")

    def resample_data(self):
        try:
            resampled_data = self.tick_data.resample('5S').agg({'Bid': ['first', 'max', 'min', 'last']}).ffill()
            if not resampled_data.empty:
                print("\nResampled Data (5-second OHLC):")
                print(resampled_data)
                
                update_chart(resampled_data)
                update_latest_data(resampled_data)
        except Exception as e:
            print(f"Error resampling data: {e}")

def update_latest_data(resampled_data):
    global latest_data

    formatted_times = resampled_data.index.to_pydatetime().tolist()
    formatted_times = [dt.isoformat() for dt in formatted_times]

    tenkan_values = [None] * len(formatted_times)
    kijun_values = [None] * len(formatted_times)

    if len(resampled_data) >= 9:
        recent_highs = resampled_data['Bid']['max'].rolling(window=9).max()
        recent_lows = resampled_data['Bid']['min'].rolling(window=9).min()
        tenkan_line = (recent_highs + recent_lows) / 2
        tenkan_values[8:] = tenkan_line.dropna().tolist()

    if len(resampled_data) >= 26:
        kijun_highs = resampled_data['Bid']['max'].rolling(window=26).max()
        kijun_lows = resampled_data['Bid']['min'].rolling(window=26).min()
        kijun_line = (kijun_highs + kijun_lows) / 2
        kijun_values[25:] = kijun_line.dropna().tolist()

    latest_data = {
        'times': formatted_times,
        'open': resampled_data['Bid']['first'].tolist(),
        'high': resampled_data['Bid']['max'].tolist(),
        'low': resampled_data['Bid']['min'].tolist(),
        'close': resampled_data['Bid']['last'].tolist(),
        'tenkan': tenkan_values,
        'kijun': kijun_values,
        'count': len(formatted_times) 
    }

def update_chart(resampled_data):
    times = resampled_data.index
    open_prices = resampled_data['Bid']['first']
    high_prices = resampled_data['Bid']['max']
    low_prices = resampled_data['Bid']['min']
    close_prices = resampled_data['Bid']['last']

    fig = go.Figure(data=[go.Candlestick(
        x=times,
        open=open_prices,
        high=high_prices,
        low=low_prices,
        close=close_prices
    )])

    # Tenkan-sen line
    if len(latest_data.get('tenkan', [])) > 0:
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(latest_data['times']),
            y=latest_data['tenkan'],
            mode='lines',
            name='Tenkan-sen',
            line=dict(color='blue')
        ))

    # Kijun-sen line
    if len(latest_data.get('kijun', [])) > 0:
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(latest_data['times']),
            y=latest_data['kijun'],
            mode='lines',
            name='Kijun-sen',
            line=dict(color='red')
        ))

    fig.update_layout(
        template='plotly_dark',
        title='CLOUD TEST',
        xaxis_title='Time',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        height=600
    )

    html_content = '''
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script>
            var layout = {
                template: 'plotly_dark',
                title: 'Cloud Test',
                xaxis: { title: 'Time' },
                yaxis: { title: 'Price' },
                xaxis_rangeslider: { visible: false },
                height: 600
            };

            function fetchData() {
                fetch('/latest-data')
                .then(response => response.json())
                .then(data => {
                    var trace1 = {
                        x: data.times,
                        open: data.open,
                        high: data.high,
                        low: data.low,
                        close: data.close,
                        type: 'candlestick',
                        name: 'Candlestick'
                    };
                    
                    var trace2 = {
                        x: data.times,
                        y: data.tenkan,
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Tenkan-sen',
                        line: { color: 'blue' }
                    };
                    
                    var trace3 = {
                        x: data.times,
                        y: data.kijun,
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Kijun-sen',
                        line: { color: 'red' }
                    };

                    Plotly.react('chart', [trace1, trace2, trace3], layout);

                    // Update candle counter
                    document.getElementById('candleCount').innerText = 'Number of Candles: ' + data.count;
                })
                .catch(error => {
                    console.error('Error fetching or plotting data:', error);
                });
            }

            setInterval(fetchData, 5000);  // every 5 seconds
        </script>
    </head>
    <body>
        <div id="chart"></div>
        <div id="candleCount" style="margin-top: 20px; font-size: 18px; color: white;"></div>
        <script>
            fetchData();  // Initial data fetch
        </script>
    </body>
    </html>
    '''

    with open(HTML_FILE, 'w') as f:
        f.write(html_content)

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/latest-data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(latest_data).encode())
        else:
            super().do_GET()

def start_server():
    Handler = MyHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        httpd.serve_forever()

def start_streaming():
    ''' Start streaming data '''
    my_oanda = MyOanda("oanda.cfg")
    my_oanda.stream_data(instrument='XAU_USD', stop=1050)
    while True:
        time.sleep(0.0001) 

threading.Thread(target=start_server, daemon=True).start()
threading.Thread(target=start_streaming, daemon=True).start()

webbrowser.open('http://localhost:8000/ichimoku.html')

root = tk.Tk()
root.withdraw() 
root.mainloop()
