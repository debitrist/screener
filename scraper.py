import requests
import pandas as pd
import datetime
import json
from pprint import pprint
from urllib.request import urlopen
from urllib.parse import urlencode

url = 'https://query1.finance.yahoo.com/v7/finance/options/OKTA'
r = requests.get(url).json()
pprint(r)
calls = r['optionChain']['result'][0]['options'][0]['calls']
calls = pd.DataFrame.from_dict(calls)
print(calls)

calls.to_csv('test.csv')

url1 = 'https://query1.finance.yahoo.com/v8/finance/chart/SPY?region=US&lang=en-US&includePrePost=false&interval=5m&range=20d&corsDomain=finance.yahoo.com&.tsrc=finance'
r1 = requests.get(url1).json()
quote = r1['chart']['result'][0]['indicators']['quote'][0]
quote1=pd.DataFrame.from_dict(quote)
quote1['Date']=[datetime.datetime.fromtimestamp(int(i)).strftime('%Y-%m-%d %H:%M:%S') for i in r1['chart']['result'][0]['timestamp']]
quote1=quote1.set_index('Date')
quote1.to_csv('quote1.csv')

### Historical Earnings Date
df = pd.read_html("https://finance.yahoo.com/calendar/earnings?symbol=veev")
earnings = df[0]['Earnings Date']
earningstiming = [test[i][-6:-3] for i in range(0,len(test))]
print(earningstiming)
print(earnings)




def parse():
    host   = 'https://query1.finance.yahoo.com'
    #host   = 'https://query2.finance.yahoo.com'  # try if above doesn't work
    path   = '/v10/finance/quoteSummary/%s' % 'okta'
    params = {
        'formatted' : 'true',
        #'crumb'     : 'ILlIC9tOoXt',
        'lang'      : 'en-US',
        'region'    : 'US',
        'modules'   : 'earningsTrend',
        'domain'    : 'finance.yahoo.com'
    }

    response = urlopen('{}{}?{}'.format(host, path, urlencode(params)))
    data = json.loads(response.read().decode())
    pprint(data)
    print(data)

if __name__ == '__main__':
    parse()

