from flask import Flask, render_template, request
import requests
import pandas as pd
import numpy as np
import btalib
import nbformat
import ta
import csv
import base64
import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# import mplfinance
import plotly.graph_objs as go   

matplotlib.use('Agg')
app = Flask(__name__)   

@app.route("/")
def home():
    # read the ticker symbols from the csv file
    # take first column and make it a list using pandas 
    tickers = pd.read_csv('listings.csv')['    Symbol'].str.strip()
    tickers = tickers.tolist()
    selected_ticker = request.args.get("ticker")

    

    return render_template("home.html", tickers=tickers)


@app.route("/submit", methods=["POST"])
def submit():
    ticker = request.form["ticker"]
    
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
    fig, axlist = mpf.plot(df, type='candle', style='charles', title=f'{ticker} Price Chart', ylabel='Price', mav=(20, 50), returnfig=True)
    candlestick_file = f'static/{ticker}_candlestick.png'
    plt.savefig(candlestick_file)
    
    # plot the RSI and MACD indicators
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(f'{ticker} Indicators')
    ax.set_ylabel('Indicator')
    df['rsi'].plot(ax=ax, label='RSI')
    df[['macd', 'macd_signal']].plot(ax=ax, label='MACD')
    plt.tight_layout()
    indicators_file = f'static/{ticker}_indicators.png'
    plt.savefig(indicators_file)
    plt.close(fig)
    
    dcf_response = requests.get(f'https://financialmodelingprep.com/api/v3/company/discounted-cash-flow/{ticker}?apikey=9f3756cdb13a16fa00d67f3e7411c576')
    
    
    dcf_data = dcf_response.json()
    
    ent_res = requests.get(f'https://financialmodelingprep.com/api/v3/enterprise-values/{ticker}?apikey=9f3756cdb13a16fa00d67f3e7411c576')
    ent_data = ent_res.json()
    # show enterprise value in table 
    ent_data = ent_data[0]
    ent_value = ent_data.get('enterpriseValue')
   


    
    # dcf_data = dcf_data[0]
    # dcf = dcf_data.get('dcf')
    # stock_price = dcf_data.get('Stock Price')
    
    # Pass the image file paths to the template
    # return render_template("results.html", ticker=ticker, candlestick_file=candlestick_file, indicators_file=indicators_file, data=df.to_json())
    return render_template(
        "results.html",
        ticker=ticker,
        candlestick_file=candlestick_file,
        indicators_file=indicators_file,
        data=df.to_json(),
        dcf=dcf_data['dcf'],
        stock_price=dcf_data['Stock Price'],
        ent_value=ent_value
        
    
    )

@app.route("/get_dcf/<ticker>")
def get_dcf(ticker):
    url = f"https://financialmodelingprep.com/api/v3/company/discounted-cash-flow/{ticker}?apikey=YOUR_API_KEY"
    response = requests.get(url)
    data = response.json()
    dcf = data[0]['dcf']
    stock_price = data[0]['Stock Price']
    return f"The DCF for {ticker} is {dcf} and the stock price is {stock_price}."

@app.route("/home")
def return_home():
    return render_template("home.html", tickers=tickers, ticker="")    

  