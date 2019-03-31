import pandas as pd
import numpy as np
import pandas_datareader.data as web
import datetime
import quandl
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

quandl.ApiConfig.api_key = "zFuFxv3joR9sQ7uYLYoZ"

df = pd.read_csv('watchlist.csv',error_bad_lines=False)

print(df)

symbol=df['Tickers'].tolist()
sourcelist=df['Source'].tolist()

d = {ticker: {} for ticker in symbol}

for ticker,source in zip(symbol,sourcelist):
    try:
        d[ticker]['px']= web.DataReader(ticker, source, datetime.datetime(2019, 1, 1), datetime.datetime.now())
        bars = d[ticker]['px']
        high_low = np.array(bars['High'] - bars['Low'])
        high_yc = abs(bars['High'] - bars['Close'].shift())
        low_yc = abs(bars['Low'] - bars['Close'].shift())
        bars['TR'] = np.dstack((high_low, high_yc, low_yc)).max(2)[0]
        bars['ATR'] = bars['TR'].rolling(20).mean()
        bars['ATR X']=bars['TR']/bars['ATR']
        bars['% Daily'] = bars['Close'].pct_change()
        bars['% Daily X']=bars['% Daily']/bars['% Daily'].rolling(20).std()
        bars['count']=np.where((bars['ATR X'] > 2) | (bars['% Daily X']>2) | (bars['% Daily X']<-2), 1, 0)
    except:
        print("Cant find "+ticker)
        del d[ticker]

summtickers = d.keys()

summarytable = pd.DataFrame([[d[ticker]['px']['Close'][-1],
                              d[ticker]['px']['TR'][-1],
                              d[ticker]['px']['ATR'][-1],
                              d[ticker]['px']['ATR X'][-1],
                              d[ticker]['px']['% Daily'][-1]*100,
                              d[ticker]['px']['% Daily X'][-1]] for ticker in summtickers], columns = ['Close', 'TR', 'ATR', 'ATR X', '% Daily', '% Daily X'], index=summtickers).round(2)

watchlistbreadth = sum([d[ticker]['px']['count'] for ticker in summtickers])

print(watchlistbreadth)

summarytablefiltered = summarytable[(summarytable['ATR X'] > 2) | (summarytable['% Daily X']>2) | (summarytable['% Daily X']<-2)]
print(summarytablefiltered)



sender_email = "stocktrackerforjk@gmail.com"
receiver_email = "noel123@gmail.com"
password = input("Type your password and press enter:")

message = MIMEMultipart("alternative")
message["Subject"] = "JK Stock Tracker"
message["From"] = sender_email
message["To"] = receiver_email

# Create the plain-text and HTML version of your message
text = """\
Hi,
"""
html = """\
<html>
  <body>
    <p>Hi,<br>
       Daily Movers > 2x 20 day ATR / 2x 20 day % Daily Returns Std Dev
    </p>{}
  </body>
</html>
""".format(summarytablefiltered.to_html())

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)

# Create secure connection with server and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )
