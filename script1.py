import requests
import pandas as pd
import numpy as np
import btalib
import nbformat
import ta
import matplotlib.pyplot as plt
import mplfinance as mpf
import plotly.graph_objs as go    

# get user input for the ticker symbol
ticker = input("Enter a ticker symbol: ") 

# define the API endpoint
url = "https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?apikey=9f3756cdb13a16fa00d67f3e7411c576"

   

# retrieve the historical data for the ticker from the API
response = requests.get(url.format(ticker=ticker))
data = response.json()['historical']

# create a dataframe from the data
df = pd.DataFrame.from_dict(data)

# convert the date column to a datetime object
df['date'] = pd.to_datetime(df['date'])

# set the index of the dataframe to the date column
df.set_index('date', inplace=True)

# calculate the technical indicators
df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
df['macd'] = ta.trend.MACD(df['close']).macd()
df['macd_signal'] = ta.trend.MACD(df['close']).macd_signal()

# plot the candlestick chart
mpf.plot(df, type='candle', style='charles', title=f'{ticker} Price Chart', ylabel='Price', mav=(20, 50))

# plot the RSI and MACD indicators
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_title(f'{ticker} Indicators')
ax.set_ylabel('Indicator')
df['rsi'].plot(ax=ax, label='RSI')
df[['macd', 'macd_signal']].plot(ax=ax, label='MACD')

# set the legend and show the plot
ax.legend()
plt.show()