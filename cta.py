import quandl
import pandas as pd
import pandas_datareader.data as web
import datetime
import numpy as np

quandl.ApiConfig.api_key = "zFuFxv3joR9sQ7uYLYoZ"


symbol = ['spy','qqq','iwm','^HSI']

d = {ticker: {} for ticker in symbol}

windowlist = ['2W','1M','3M','6M','1Y']
windowper = [10,21,63,126,252]
voltarget = 12

for ticker in symbol:
    print(ticker)
    d[ticker]['px'] = web.DataReader(ticker, 'yahoo', datetime.datetime(1995, 1, 1), datetime.datetime.now())

    df = d[ticker]['px']
    df['Close Ret'] = df['Close'].pct_change()

    for x,y in zip(windowlist,windowper):
        df[x]=df['Close'].shift(y)
        df[x+str('momret')]=df['Close']/df[x]-1
        df[x+str('stdev')]=voltarget/(df['Close Ret'].rolling(y).std()*100*(252**0.5))
        df[x+str('momsig')] = np.where(df[x+str('momret')].shift()>0, df['Close Ret'], np.where(df[x+str('momret')].shift()<0,-df['Close Ret'],0))
        df[x+str('momsigLO')] = np.where(df[x+str('momret')].shift()>0, df['Close Ret'], 0)
        df[x+str('simret')]=np.exp(np.log(1+(df[x+str('momsig')]*df[x+str('stdev')].shift())).cumsum())
        df[x+str('simretLO')]=np.exp(np.log(1+(df[x+str('momsigLO')]*df[x+str('stdev')].shift())).cumsum())



    pricelvls = [df.iloc[-1]['Close']]

    for window in windowlist:
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

d['spy']['px'].to_csv('test.csv')

