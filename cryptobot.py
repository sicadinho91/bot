import requests
import json
import time
import datetime
import csv
import numpy as np
import pandas as pd

def retrieve(url, params=None):
    r = requests.get(url, params=params)
    data = r.json()
    return data
    
def ema(df):
    per = [5, 12, 20, 26]
    for i in per:
        df['%i EMA'%i] = df['rate'].ewm(ignore_na=False, span=i, min_periods=i, adjust=True).mean()
    df['12-26 EMA'] = df['12 EMA'] - df['26 EMA']
    return df

def sma(df):
    per = [5, 6, 10, 20]
    for i in per:
        df['%i SMA'%i] = df['rate'].rolling(window=i).mean()
        df['Delta_%i SMA' %i] = df['%i SMA'%i] - df['%i SMA'%i].shift(-1)
    return df

def macd(df):
    i = 9
    df['macd line'] = df['12 EMA'] - df['26 EMA']
    df['Delta_macd line'] = df['macd line'] - df['macd line'].shift(-1)
    df['macd signal'] = df['macd line'].ewm(ignore_na=False,span=i,min_periods=i,adjust=True).mean()
    df['macd histogram'] = df['macd line'] - df['macd signal']
    return df

def move(df):
    i, b = 3, 9
    df['Momentum'] = df['rate'] - df['rate'].shift(i)
    df['ROC']=((df['rate']-df['rate'].shift(b))/df['rate'].shift(b))*100
    return df

def bband(df):
    per = [5, 10, 20]
    for i in per:
        std = df['rate'].rolling(window=i).std()
        df['%i upper band'%i] = df['%i SMA'%i] + std
        df['%i lower band'%i] = df['%i SMA'%i] - std
        df['%i middle band'%i] = df['%i SMA'%i]
    return df
    
def get_tickers(url):
    tickers = []
    t = retrieve(url)
    t = t.keys()
    for i in t:
        if 'USDT' in i:
            tickers.append(i)
    return tickers
    
def get_trades(tickers):
    data = pd.DataFrame()
    for i in tickers:
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        before = int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=20)).timetuple()))
        url = 'https://poloniex.com/public?command=returnTradeHistory&currencyPair={}&start={}&end={}'.format(i,before,now)
        trades = pd.DataFrame(retrieve(url))
        trades['ticker'] = i
        trades['rate'] = trades['rate'].astype('float')
        ema(trades)
        sma(trades)
        macd(trades)
        move(trades)
        bband(trades)
        trades = trades[np.isfinite(trades['macd signal'])]
        print(trades)
        if len(data)==0:
            data = trades
        else:
            data = data.append(trades)
        print(trades)
    data['date'] = pd.to_datetime(data['date'])-pd.Timedelta(hours=5)
    return data
        
def get_chart(tickers):
    data = pd.DataFrame()
    now = int(time.mktime(datetime.datetime.now().timetuple()))
    before = int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=20)).timetuple()))
    for i in tickers:
        for p in [300, 900, 1800, 7200, 14400, 86400]:
            url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'.format(i,before,now, p)
            charts = pd.DataFrame(retrieve(url))
            charts['ticker'] = i
            charts['timedelta'] = p
            if len(data)==0:
                data = charts
            else:
                data = data.append(charts)
            print(charts)
    data['datetime'] = pd.to_datetime(data['date'], unit='s')
    return data       
              
def poloniex():
    t = get_tickers('https://poloniex.com/public?command=returnTicker')
    print(t)
    trades = get_trades(t)
    charts = get_chart(t)
    trades.to_excel('./Outputs/bot_trades %s.xlsx' %datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S'))
    charts.to_excel('./Outputs/bot_charts %s.xlsx' %datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S'))
    t_charts={}
    t_trades={}
    for i in t:
        t_charts[i] = charts[charts['ticker']==i]
        t_trades[i] = trades[trades['ticker']==i]
    print(t_charts)
    print(t_trades)
    #t_charts['USDT_BTC'].loc[t_charts['USDT_BTC']['timedelta']==300]

def main():
    start_time = time.time()
    print('Exchange: Poloniex')
    poloniex()
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()