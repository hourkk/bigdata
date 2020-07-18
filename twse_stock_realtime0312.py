#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from urllib.request import urlopen
import requests
import json
from sqlalchemy import create_engine
#from sqlalchemy.types import Integer,Time,FLOAT,VARCHAR,Date
import sched
import datetime


#連結sql
#linux mysql -> mysql+pymysql
engine = create_engine('mysql://' 
                       ')
                       #帳號             密碼                   host                       資料庫名稱


#當天上市公司

res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
df = pd.read_html(res.text)[0]
df.columns = df.iloc[0]
df=df.iloc[2:]
stock_dict={}
for i in df['有價證券代號及名稱']:
    if len(i.split( )) <2:
        break
    stock_dict[i.split( )[0]]=i.split( )[1]

#設定開始結束
start_time = datetime.datetime.strptime(str(datetime.datetime.now().date())+'9:00', '%Y-%m-%d%H:%M')
end_time =  datetime.datetime.strptime(str(datetime.datetime.now().date())+'13:30', '%Y-%m-%d%H:%M')    

#抓取資訊
def stock_crawler():
    c=1
    sc=list()
    print('start'+str(datetime.datetime.now()))
    for i in stock_dict:
        #一次最多165個左右
        if c %165!=0 and c!=len(stock_dict):
            sc.append(i)
            c+=1
            continue

        sc.append(i)
        c+=1
        stock_list = '|'.join('tse_{}.tw'.format(target) for target in sc) 
        sc=list()
        query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="+ stock_list

        try:
            data = json.loads(urlopen(query_url).read())
            columns = ['c','n','d','t','z','tv','v','o','h','l','y']
            df = pd.DataFrame(data['msgArray'], columns=columns)
        except:
            print(i+' err')
            continue
        df.columns = ['sid','name','date','time','price','volume','accumulation','open','max','min','close']
        #types={'sid': Integer(),'name':VARCHAR(),'date':Date(),'time':Time(),'price':FLOAT() ,'volume': Integer(),'accumulation': Integer(),'open':FLOAT(),'max':FLOAT(),'min':FLOAT(),'close':FLOAT()}
        df.to_sql('stock_realtime', con=engine, if_exists='append',index=False)
        
        print(str(round(c/165, 0))+' finish')
                    #資料庫名稱
    
    print('end'+str(datetime.datetime.now()))
    # 紀錄更新時間
    time = datetime.datetime.now()  
    #開始結束時間
    if time >= start_time and time <= end_time:
        s.enter(10, 0, stock_crawler, argument=())

#開始排成
s = sched.scheduler()
s.enter(0, 0, stock_crawler, argument=())
s.run()