import requests
import json
import time
import datetime
import pandas as pd

def retrieve(url, params=None):
    r = requests.get(url, params=params)
    data = r.json()
    return data
    
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
        if len(data)==0:
            data = trades
        else:
            data = data.append(trades)
        print(trades)
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
    
def main():
    start_time = time.time()
    print('Exchange: Poloniex')
    poloniex()
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()