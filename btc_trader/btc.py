import yfinance as yf
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import io
import base64
import os

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def calculate_wma(data, window):
    weights = np.arange(1, window + 1)
    return data.rolling(window).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

def calculate_hma(data, window):
    half_window_wma = calculate_wma(data, window // 2)
    full_window_wma = calculate_wma(data, window)
    hma_intermediate = 2 * half_window_wma - full_window_wma
    return calculate_wma(hma_intermediate, int(np.sqrt(window)))

def generate_chart_html(symbol, data, sma, hma, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    bar_numbers = range(len(data))
    ax.plot(bar_numbers, data['Close'], label='Price', color='black')
    ax.plot(bar_numbers, sma, label='20 SMA', color='black')
    ax.plot(bar_numbers, hma, label='14 HMA', color='red')
    ax.set_title(f"{symbol} - {title}")
    ax.legend(loc='upper left')
    plt.tight_layout()
    
    # Save the chart as an HTML page
    chart_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{symbol} Chart</title>
    </head>
    <body>
        <h1>{symbol} - {title}</h1>
        <img src="data:image/png;base64,{base64.b64encode(io.BytesIO(plt_to_png(fig)).getvalue()).decode('utf-8')}" />
    </body>
    </html>
    """
    plt.close(fig)

    with open(f"{symbol}_chart.html", "w") as f:
        f.write(chart_html)

def plt_to_png(fig):
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    return buf.getvalue()

def get_stock_data(symbol):
    ticker = yf.Ticker(symbol)
    stock_data = ticker.history(interval='1m', start=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))
    sma = calculate_sma(stock_data['Close'], 20)
    hma = calculate_hma(stock_data['Close'], 14)
    
    generate_chart_html(symbol, stock_data[-120:], sma[-120:], hma[-120:], "2 Hour Chart")

if __name__ == '__main__':
    # Choose a single symbol to generate the chart
    symbol = 'BTC-USD'  # You can change this to any symbol
    get_stock_data(symbol)
