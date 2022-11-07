import requests
import pandas as pd
import time
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler()

#colunm_name
#[price│quantity│type│timestamp]

def send_sms(msg) :

    API_key = '2pq3omszojd4g9838hdtczxw2lh7roo2'

    payload = {
        "key": API_key,
        "user_id": 'kys2312',
        "sender": '01046552302',
        "receiver": '01046552302',
        "msg": msg,
        "testmode_yn":'Y'
    }

    try:
        response = requests.post('https://apis.aligo.in:443', data=payload)
        print(response.json())
        
    except:
        print("alert message didn't sent")

@sched.scheduled_job('interval', seconds=1, id='req')
def req():
    try:
        url = "https://api.upbit.com/v1/orderbook?markets=KRW-BTC"

        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)

        ts = str(datetime.now())

        order= response.json()[0]['orderbook_units']

        order_bid_df = pd.DataFrame(columns=['bid_price','bid_size'], data=order)
        order_bid_df.columns=['price','quantity']
        order_bid_df.sort_values(by=['price'],axis=0,ascending=False)
        order_bid_df=order_bid_df.assign(side = 0, timestamp=ts)
        order_bid_df=order_bid_df[0:15]

        order_ask_df = pd.DataFrame(columns=['ask_price', 'ask_size'], data=order)
        order_ask_df.columns=['price','quantity']
        order_ask_df.sort_values(by=['price'],axis=0,ascending=True)
        order_ask_df=order_ask_df.assign(side = 1, timestamp=ts)
        order_ask_df=order_ask_df[0:15]
        
        order_df = pd.concat([order_bid_df,order_ask_df], axis=0).reset_index(drop=True)
    except:
        order_df = pd.DataFrame([[0,0,0,ts]],columns=['price','quantity','side', 'timestamp'])
        for i in range(29):
            order_df = pd.concat([order_df,pd.DataFrame([[0,0,0,ts]],columns=['price','quantity','side', 'timestamp'])])
        send_sms('Error occured. check server')
        
    uri = './data/'+str(int(time.time()))+'.csv'
    
    order_df.to_csv(uri,index=False)

if __name__ == "__main__" : 
    sched.start()
    while True:
        time.sleep(1)    
