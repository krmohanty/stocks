
# coding: utf-8

# In[1]:


import pandas as pd
import datetime
import numpy as np
import os


# In[2]:


os.chdir("C:\\Users\\mohantyk\\lab\\stocks")

with open('p.txt', 'r') as myfile:
    pwd=myfile.read().replace('\n', '')


# In[3]:


#Alert %
profit = 25
loss = 2


# In[4]:


ref_table=pd.read_csv('ref_table.csv')


# In[5]:


ref_table['ref_date']=pd.to_datetime(ref_table.ref_date)


# In[6]:


stocks_to_track=list(ref_table.stock.values)

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


# In[7]:


df2=df.merge(ref_table,on='stock')


# In[8]:


df2['date']=df2.timestamp.dt.date


df2['date']=pd.to_datetime(df2.date)


# In[9]:


max_date=df2.groupby('stock',as_index=False).agg({'date':'max'})

max_date.rename(columns={'date':'max_date'},inplace=True)


# In[10]:


df3=df2.merge(max_date,on='stock')

now=df3.loc[df3.date==df3.max_date,['stock','close','date']]

now.rename(columns={'close':'current_price'},inplace=True)


# In[11]:


data=ref_table.merge(now,on='stock')


# In[12]:


data['days']=data.date-data.ref_date


# In[13]:


data['perc_diff']=(data.current_price/data.cost -1)*100

data['profit_flag'] = np.where(data.perc_diff >= profit,1,0)

data['loss_flag'] = np.where(data.perc_diff <= loss,1,0)


# In[ ]:


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

