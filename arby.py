import requests
import json
import time
import datetime
import pandas as pd

def retrieve(url, params=None):
    r = requests.get(url, params=params)
    data = r.json()
    return data
    
def ir():
    irdf = []
    irprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    for i in ['xbt', 'eth']:
        url = 'https://api.independentreserve.com/Public/GetMarketSummary?primaryCurrencyCode={}&secondaryCurrencyCode=usd'.format(i)
        irdata = retrieve(url)
        irdf.append(irdata)
        if i == 'xbt':
            irprice['BTC']= float(irdata['LastPrice'])
            irprice['bid_btc']= float(irdata['CurrentHighestBidPrice'])
            irprice['ask_btc']= float(irdata['CurrentLowestOfferPrice'])
        else:
            irprice['ETH'] = float(irdata['LastPrice'])
            irprice['bid_eth']= float(irdata['CurrentHighestBidPrice'])
            irprice['ask_eth']= float(irdata['CurrentLowestOfferPrice'])
    irprice['exchange'] = ('independent reserve')
    #print(irprice)
    return irprice

def polo():
    polodf = []
    poloprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    url = 'https://poloniex.com/public?command=returnTicker'
    polodata = retrieve(url)
    polodf.append(polodata)
    for i in ['BTC', 'ETH']:
        poloprice[i] = (float(polodata['USDT_'+i]['last']))
        poloprice['bid_%s'%i.lower()] = (float(polodata['USDT_'+i]['highestBid']))
        poloprice['ask_%s'%i.lower()] = (float(polodata['USDT_'+i]['lowestAsk']))
    poloprice['exchange'] = ('poloniex')
    #print(poloprice)
    return poloprice
    
def gdax():
    gdaxdf = []
    gdaxprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    for i in ['BTC-USD', 'ETH-USD']:
        url = 'https://api.gdax.com/products/{}/ticker'.format(i)
        gdaxdata = retrieve(url)
        gdaxdf.append(gdaxdata)
        if i == 'BTC-USD':
            gdaxprice['BTC'] = float(gdaxdata['price'])
            gdaxprice['bid_btc'] = float(gdaxdata['bid'])
            gdaxprice['ask_btc'] = float(gdaxdata['ask'])
        else:
            gdaxprice['ETH'] = float(gdaxdata['price'])
            gdaxprice['bid_eth'] = float(gdaxdata['bid'])
            gdaxprice['ask_eth'] = float(gdaxdata['ask'])
    gdaxprice['exchange'] = ('gdax')
    #print (gdaxprice)
    return gdaxprice

def kraken():
    krakendf = []
    krakenprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    for i in ['XBTUSD', 'ETHUSD']:
        url = 'https://api.kraken.com/0/public/Ticker?pair=%s'%i
        krakendata = retrieve(url)
        krakendf.append(krakendata)
        if i == 'XBTUSD':
            krakenprice['BTC'] = float(krakendata['result']['XXBTZUSD']['c'][0])
            krakenprice['bid_btc'] = float(krakendata['result']['XXBTZUSD']['b'][0])
            krakenprice['ask_btc'] = float(krakendata['result']['XXBTZUSD']['a'][0])
        else:
            krakenprice['ETH'] = float(krakendata['result']['XETHZUSD']['c'][0])
            krakenprice['bid_eth'] = float(krakendata['result']['XETHZUSD']['b'][0])
            krakenprice['ask_eth'] = float(krakendata['result']['XETHZUSD']['a'][0])
    krakenprice['exchange'] = ('kraken')
    #print (krakenprice)
    return krakenprice

def liqui():
    liquidf = []
    liquiprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    for i in ['btc_usdt', 'eth_usdt']:
        url = 'https://api.liqui.io/api/3/ticker/%s'%i
        success = False
        while success == False:
            liquidata = retrieve(url)
            if 'success' in liquidata:
                time.sleep(2.0)
            else:
                success = True
        liquidf.append(liquidata)
        if i == 'btc_usdt':
            liquiprice['BTC'] = float(liquidata[i]['last'])
            liquiprice['bid_btc'] = float(liquidata[i]['buy'])
            liquiprice['ask_btc'] = float(liquidata[i]['sell'])
            time.sleep(2.0)
        else:
            liquiprice['ETH'] = float(liquidata[i]['last'])
            liquiprice['bid_eth'] = float(liquidata[i]['buy'])
            liquiprice['ask_eth'] = float(liquidata[i]['sell'])
    liquiprice['exchange'] = ('liqui')
    #print (liquiprice)
    return liquiprice
    
def kucoin():
    kucoindf = []
    kucoinprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    for i in ['BTC-USDT', 'ETH-USDT']:
        url = 'https://api.kucoin.com/v1/open/tick?symbol=%s'%i
        kucoindata = retrieve(url)
        kucoindf.append(kucoindata)
        if i == 'BTC-USDT':
            kucoinprice['BTC'] = float(kucoindata['data']['lastDealPrice'])
            kucoinprice['bid_btc'] = float(kucoindata['data']['buy'])
            kucoinprice['ask_btc'] = float(kucoindata['data']['sell'])
        else:
            kucoinprice['ETH'] = float(kucoindata['data']['lastDealPrice'])
            kucoinprice['bid_eth'] = float(kucoindata['data']['buy'])
            kucoinprice['ask_eth'] = float(kucoindata['data']['sell'])
    kucoinprice['exchange'] = ('kucoin')
    #print (kucoinprice)
    return kucoinprice
    
def gatecoin():
    gatecoindf = []
    gatecoinprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    for i in ['BTCUSD', 'ETHUSD']:
        url = 'https://api.gatecoin.com/Public/LiveTicker/%s'%i
        url2 = 'https://api.gatecoin.com/Public/MarketDepth/%s'%i
        gatecoinob = retrieve(url2)
        bids = pd.DataFrame(gatecoinob['bids'])
        bids['value'] = bids['price']*bids['volume']
        bids['cumulative'] = bids['value'].cumsum()
        asks = pd.DataFrame(gatecoinob['asks'])
        asks['value'] = asks['price']*asks['volume']
        asks['cumulative'] = asks['value'].cumsum()
        gatecoindata = retrieve(url)
        gatecoindf.append(gatecoindata)
        if i == 'BTCUSD':
            gatecoinprice['BTC'] = float(gatecoindata['ticker']['last'])
            gatecoinprice['bid_btc'] = bids[bids.cumulative > 25000].iloc[0]['price']
            gatecoinprice['ask_btc'] = asks[asks.cumulative > 25000].iloc[0]['price']
        else:
            gatecoinprice['ETH'] = float(gatecoindata['ticker']['last'])
            gatecoinprice['bid_eth'] = bids[bids.cumulative > 25000].iloc[0]['price']
            gatecoinprice['ask_eth'] = asks[asks.cumulative > 25000].iloc[0]['price']          
    gatecoinprice['exchange'] = ('gatecoin')
    #print (gatecoinprice)
    return gatecoinprice   
    
def binance():
    binancedf = []
    binanceprice = {'BTC':[], 'ETH':[],'exchange':[], 'bid_btc':[], 'ask_btc':[], 'bid_eth':[], 'ask_eth':[]}
    url = 'https://api.binance.com/api/v3/ticker/bookTicker'
    binancedata = pd.DataFrame(retrieve(url))
    binancedf.append(binancedata)
    binanceprice['bid_btc'] = float(binancedata[binancedata['symbol']=='BTCUSDT']['bidPrice'])
    binanceprice['ask_btc'] = float(binancedata[binancedata['symbol']=='BTCUSDT']['askPrice'])
    binanceprice['bid_eth'] = float(binancedata[binancedata['symbol']=='ETHUSDT']['bidPrice'])
    binanceprice['ask_eth'] = float(binancedata[binancedata['symbol']=='ETHUSDT']['askPrice'])         
    binanceprice['exchange'] = ('binance')
    url = 'https://api.binance.com/api/v3/ticker/price'
    binancedata = pd.DataFrame(retrieve(url))
    binancedf.append(binancedata)
    binanceprice['BTC'] = float(binancedata[binancedata['symbol']=='BTCUSDT']['price'])
    binanceprice['ETH'] = float(binancedata[binancedata['symbol']=='ETHUSDT']['price'])
    #print (binanceprice)
    return binanceprice  
    
def main():
    start_time = time.time()
    print ('''
    ARBITRAGE MODEL
    ''')
    master = []
    i = ir()
    p = polo()
    g = gdax()
    k = kraken()
    l = liqui()
    ku = kucoin()
    ga = gatecoin()
    b = binance()
    master.append(i)
    master.append(p)
    master.append(g)
    master.append(k)
    master.append(l)
    master.append(ku)
    master.append(ga)
    master.append(b)
    master = pd.DataFrame(master)
    print('BTC opportunity: ', round((((master['bid_btc'].max()/master['ask_btc'].min()) - 1) * 100), 2),'%')
    print('ETH opportunity: ', round((((master['bid_eth'].max()/master['ask_eth'].min()) - 1) * 100), 2),'%')
    master['btc return %'] = round((master['bid_btc'].max() - master['ask_btc'])/master['ask_btc'],4)*100
    master['eth return %'] = round((master['bid_eth'].max() - master['ask_eth'])/master['ask_eth'],4)*100
    print(master)
    master.to_excel('./Outputs/arby_matrix %s.xlsx' %datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S'))
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()