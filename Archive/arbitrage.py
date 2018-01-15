#crypto arbitrage model
#main.py
import requests
import json
import time
from datetime import datetime
import pandas as pd

def main():
    start_time = time.time()
    print(r"""   
    
    |@|@|@|@|           |@|@|@|@|
    |@|@|@|@|   _____   |@|@|@|@|
    |@|@|@|@| /\_T_T_/\ |@|@|@|@|
    |@|@|@|@||/\ T T /\||@|@|@|@|
     ~/T~~T~||~\/~T~\/~||~T~~T\~
      \|__|_| \(-(O)-)/ |_|__|/
      _| _|    \\8_8//    |_ |_
    |(@)]   /~~[_____]~~\   [(@)|
      ~    (  |       |  )    ~
          [~` ]       [ '~]
          |~~|         |~~|
          |  |         |  |
         _<\/>_       _<\/>_
        /_====_\     /_====_\
      
             ARBITRAGE
                _           _   
               | |         | |  
      _ __ ___ | |__   ___ | |_ 
     | '__/ _ \| '_ \ / _ \| __|
     | | | (_) | |_) | (_) | |_ 
     |_|  \___/|_.__/ \___/ \__|
                           
    Christopher Sica
    
      """)
    r = requests.get('https://min-api.cryptocompare.com/data/all/exchanges')
    alldata = r.json()
    exchanges = [
        'Binance', 'BitBay', 'BitTrex', 'Bitfinex', 'Bithumb', 
        'Bitso', 'Bitstamp', 'Bleutrade', 'Cexio', 'CoinExchange', 
        'Coinbase', 'Coinfloor', 'Coinone', 'Coinroom', 'Cryptopia', 
        'EXX', 'EtherDelta', 'Exmo', 'Gatecoin', 'Gateio', 'Gemini', 
        'HitBTC', 'Korbit', 'Kraken', 'Kucoin', 'LakeBTC', 
        'Liqui', 'LiveCoin', 'Luno', 'Lykke', 'OKEX', 
        'Poloniex', 'QuadrigaCX', 'Quoine', 'Tidex', 'Yacuna', 'Yobit', 
        'Zaif', 'bitFlyer', 'itBit'
        ]
    fsym = ['BTC', 'XRP', 'ETH', 'BCH', 'ADA', 'LTC']
    tsym = fsym + ['USD', 'USDT']
    cols = []
    for val in fsym:
        for item in tsym:
            if val != item:
                cols.append(val+str('-')+item)
    output = []
    df = pd.DataFrame(index=exchanges, columns=cols)
    #print(alldata.keys())
    for key, val in alldata.items():
        e = key
        for crypt in val.keys():
            f = crypt
            for curr in alldata[key][crypt]:
                t = curr
                #print('e,f,t: ', e, f, t)
                if (e in exchanges) & (f in fsym) & (t in tsym) & (f != t):
                    r = requests.get('https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}&e={}'.format(f, t, e))
                    data = r.json()
                    price = data[t]
                    new_line = [e,f,t,price]
                    output.append(new_line)
                    df.loc[e, f+'-'+t] = price
                    print(e+'-'+f+'-'+t+' ==> ' + str(price))
    df.to_excel('./Outputs/arbitrage_matrix %s.xlsx' %datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S'))
    print("--- %s seconds ---" % (time.time() - start_time))
if __name__ == "__main__":
    main()