import pandas as pd
import datetime
import numpy as np
import os

os.chdir("C:\\Users\\mohantyk\\lab\\stocks")

with open('p.txt', 'r') as myfile:
    pwd=myfile.read().replace('\n', '')

#Alert %
profit = 1
loss = -1

ref_dates=pd.read_csv('ref_dates.csv')


ref_dates['ref_date']=pd.to_datetime(ref_dates.ref_date)


stocks_to_track=list(ref_dates.stock.values)

df_list=[]

for x in stocks_to_track:
    #print(x)
    url="https://www.alphavantage.co/query?apikey=6PFVKSN75XGEMU6S&function=TIME_SERIES_DAILY_ADJUSTED&symbol="+x+"&datatype=csv"
    #print(url)
    d1=pd.read_csv(url)
    d1['stock']=x
    df_list.append(d1)

df = pd.concat(df_list)

df['timestamp']=pd.to_datetime(df.timestamp)


df2=df.merge(ref_dates,on='stock')


df2['date']=df2.timestamp.dt.date


df2['date']=pd.to_datetime(df2.date)

ref=df2.loc[df2.date==df2.ref_date,['stock','close']]


max_date=df2.groupby('stock',as_index=False).agg({'date':'max'})

max_date.rename(columns={'date':'max_date'},inplace=True)


df3=df2.merge(max_date,on='stock')

now=df3.loc[df3.date==df3.max_date,['stock','close']]

now.rename(columns={'close':'current_price'},inplace=True)

ref.rename(columns={'close':'reference_price'},inplace=True)

data=ref.merge(now,on='stock')

data['perc_diff']=(data.current_price/data.reference_price -1)*100

data['profit_flag'] = np.where(data.perc_diff >= profit,1,0)

data['loss_flag'] = np.where(data.perc_diff <= loss,1,0)

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# me == my email address
# you == recipient's email address
me = "kirtiraj.careers@gmail.com"
you = "kr.mohanty@gmail.com"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Stock Alert"
msg['From'] = me
msg['To'] = you

# Create the body of the message (a plain-text and an HTML version).
#text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
html = data.to_html()

# Record the MIME types of both parts - text/plain and text/html.
#part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
#msg.attach(part1)
msg.attach(part2)

if (data.profit_flag.sum() > 0 or data.loss_flag.sum() >0):
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login('kirtiraj.careers', pwd)
    mail.sendmail(me, you, msg.as_string())
    mail.quit()
    print('email sent')


