import requests
import json
import time
import datetime
import numpy as np
import pandas as pd

def retrieve(url, params=None):
    r = requests.get(url, params=params)
    data = r.json()
    return data
    
def ema(df):
    per = [12, 20, 26]
    for i in per:
        df['%i EMA'%i] = df['rate'].ewm(ignore_na=False, span=i, min_periods=i, adjust=True).mean()
    df['12-26 EMA'] = df['12 EMA'] - df['26 EMA']
    return df

def sma(df):
    per = [10, 20]
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
    per = [10, 20]
    for i in per:
        std = df['rate'].rolling(window=i).std() * 2
        df['%i upper band'%i] = df['%i SMA'%i] + std
        df['%i lower band'%i] = df['%i SMA'%i] - std
        df['%i middle band'%i] = df['%i SMA'%i]
    return df
    
def strength(df):
    i = 14
    b = [14, 7]
    df['LW %R'] = ((df['high'].rolling(window=i).max()-df['rate'])/(df['high'].rolling(window=i).max()-df['low'].rolling(window=i).min()))*-100
    df['Delta_LW %R'] = df['LW %R'] - df['LW %R'].shift(-1)
    for n in b:
        delta = df['rate']-df['rate'].shift(1)
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0
        RolUp = dUp.rolling(window=n).mean()
        RolDown = dDown.rolling(window=n).mean().abs()
        RS = RolUp / RolDown
        df['RSI %i'%n] = 100-(100/(1+RS))
        df['Delta_RSI %i'%n] = df['RSI %i'%n] - df['RSI %i'%n].shift(-1)
    return df
    
def stoch(df):
    i, b = 14, 3
    df['stoch k'] = (df['rate']-df['low'].rolling(window=i).min())/(df['high'].rolling(window=i).max()-df['low'].rolling(window=i).min())*100
    df['Delta_stoch k'] = df['stoch k'] - df['stoch k'].shift(-1)
    df['stoch d'] = df['stoch k'].rolling(window=b).mean()
    df['Delta_stoch d'] = df['stoch d'] - df['stoch d'].shift(-1)
    df['slow d'] = df['stoch d'].rolling(window=b).mean()
    return df
    
def adx(df):
    hl = df['high'] - df['low']
    ahr = abs(df['high'] - df['rate'].shift(1))
    alr = abs(df['low'] - df['rate'].shift(1))
    hs = df['high'] - df['high'].shift(1)
    ls = df['low'].shift(1) - df['low']
    tr = []
    pdm = []
    ndm = []
    for i in range(0,len(hl)):
        tr.append(max(hl[i],ahr[i],alr[i]))
        if (hs[i] > ls[i]):
            pdm.append(max(hs[i],0))
            ndm.append(0)
        else:
            ndm.append(max(ls[i],0))
            pdm.append(0)
    tr, pdm, ndm = pd.Series(tr), pd.Series(pdm), pd.Series(ndm)
    tr14, pdm14, ndm14 = [], [], []
    for i in range(0,len(tr)):
        if i < 14:
            tr14.append(np.nan)
            pdm14.append(np.nan)
            ndm14.append(np.nan)
        elif i == 14:
            tr14.append(tr.loc[1:14].sum())
            pdm14.append(pdm.loc[1:14].sum())
            ndm14.append(ndm.loc[1:14].sum())
        else:
            tr14.append(tr14[i-1] - (tr14[i-1]/14) + tr[i])
            pdm14.append(pdm14[i-1] - (pdm14[i-1]/14) + pdm[i])
            ndm14.append(ndm14[i-1] - (ndm14[i-1]/14) + ndm[i])
    tr14, pdm14, ndm14 = pd.Series(tr14), pd.Series(pdm14), pd.Series(ndm14)        
    pdi14 = (100 * (pdm14/tr14))
    ndi14 = (100 * (ndm14/tr14))
    di14d = abs(pdi14 - ndi14)
    di14s = pdi14 + ndi14
    dx = pd.Series(100 * (di14d/di14s))
    adx = []
    for i in range(0,len(df['rate'])):
        if i < 14:
            adx.append(np.nan)
        elif i == 27:
            adx.append(dx.loc[14:i].mean())
        else:
            adx.append(((adx[i-1]*13)+dx.loc[i])/14)
    pdi14 = pd.Series(pdi14)
    pdi14.name = '+DI'
    ndi14 = pd.Series(ndi14)
    ndi14.name = '-DI'
    adx = pd.Series(adx)
    adx.name = 'ADX'
    df = pd.concat([df, pdi14, ndi14, adx], join='outer', axis=1)
    print(df)
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
        trades['total'] = trades['total'].astype('float')
        trades['amount'] = trades['amount'].astype('float')
        #ema(trades)
        #sma(trades)
        #macd(trades)
        #move(trades)
        #bband(trades)
        #trades = trades[np.isfinite(trades['macd signal'])]
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
    p_dict = {300:2, 900:6, 1800:12, 7200:48, 14400:96, 86400:576}
    for i in tickers:
        for p in p_dict:
            before = int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=p_dict[p])).timetuple()))
            url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'.format(i,before,now, p)
            charts = pd.DataFrame(retrieve(url))
            charts = charts.rename(columns={'close':'rate'})
            charts['ticker'] = i
            charts['timedelta'] = p
            charts['rate'] = charts['rate'].astype('float')
            ema(charts)
            sma(charts)
            macd(charts)
            move(charts)
            bband(charts)
            strength(charts)
            stoch(charts)
            charts = adx(charts)
            if len(data)==0:
                data = charts
            else:
                data = data.append(charts)
            print(charts)
    data['datetime'] = pd.to_datetime(data['date'], unit='s')
    data['Bull Bollinger Cross'] = np.where(((data['rate'] > data['20 upper band']) & (data['rate'].shift(1) < data['20 upper band'].shift(1))), 1, "")
    data['Bear Bollinger Cross'] = np.where(((data['rate'] < data['20 lower band']) & (data['rate'].shift(1) > data['20 lower band'].shift(1))), -1, "")
    data['Bull ADX'] = np.where(((data['+DI'] > data['-DI']) & (data['+DI'].shift(1) < data['-DI'].shift(1)) & (data['ADX'] > 20)), 1, "")
    data['Bear ADX'] = np.where(((data['-DI'] > data['+DI']) & (data['-DI'].shift(1) < data['+DI'].shift(1)) & (data['ADX'] > 20)), -1, "")
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
    #pd.DataFrame(charts[charts['ticker']=='USDT_ETH']).to_excel('./Outputs/eth_charts.xlsx')

def main():
    start_time = time.time()
    print('Exchange: Poloniex')
    poloniex()
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()