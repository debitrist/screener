import quandl
import pandas as pd
import pandas_datareader.data as web
import datetime
import numpy as np

quandl.ApiConfig.api_key = "zFuFxv3joR9sQ7uYLYoZ"


symbol = ['spy','qqq','iwm','^HSI']

d = {ticker: {} for ticker in symbol}

for ticker in symbol:
    print(ticker)
    d[ticker]['px'] = web.DataReader(ticker, 'yahoo', datetime.datetime(2015, 1, 1), datetime.datetime.now())
    
    df = d[ticker]['px']
    df['2W']=df['Close'].shift(10)
    df['1M']=df['Close'].shift(21)
    df['3M']=df['Close'].shift(63)
    df['6M']=df['Close'].shift(126)
    df['1Y']=df['Close'].shift(252)

    pricelvls = [df.iloc[-1]['Close']]

    for window in ['2W','1M','3M','6M','1Y']:
        pricelvls.append(df[window][-1])
        pricelvls.append(df[window][-1]+0.1)
        pricelvls.append(df[window][-1]-0.1)

    pricelvls.sort(reverse=True)

    d[ticker]['cta'] = pd.DataFrame({'% Return Req': (pricelvls/df['Close'].iloc[-1]-1)*100, 'Px Lvls': pricelvls})

    pricedf = d[ticker]['cta']
    for window in ['2W','1M','3M','6M','1Y']:
        pricedf[window] = np.where(pricedf['Px Lvls'] > df[window][-1],1,np.where(pricelvls == df[window][-1],0,-1 ))

    pricedf['pos']=np.sum(pricedf.loc[:,'2W':'1Y'], axis=1)/5*100
    d[ticker]['ctaoutput']=pricedf[pricedf['Px Lvls'] == df['Close'].iloc[-1]]

ctatable = pd.DataFrame(
    [[d[ticker]['cta']['2W'][d[ticker]['cta']['% Return Req']==0].values[0],
      d[ticker]['cta']['1M'][d[ticker]['cta']['% Return Req'] == 0].values[0],
      d[ticker]['cta']['3M'][d[ticker]['cta']['% Return Req'] == 0].values[0],
      d[ticker]['cta']['6M'][d[ticker]['cta']['% Return Req'] == 0].values[0],
      d[ticker]['cta']['1Y'][d[ticker]['cta']['% Return Req'] == 0].values[0],
      d[ticker]['cta']['pos'][d[ticker]['cta']['% Return Req'] == 0].values[0],
      round(d[ticker]['cta']['Px Lvls'][d[ticker]['cta']['% Return Req'] == 0].values[0],2),
      round(d[ticker]['cta']['Px Lvls'][d[ticker]['cta']['pos'] == -100].values[0],2),
      round(d[ticker]['cta']['Px Lvls'][d[ticker]['cta']['pos'] == 100].values[0],2)] for ticker in symbol],
    columns=['2W','1M','3M','6M','1Y','pos','lastclose','shortpx','longpx'], index=symbol)

print(ctatable)


