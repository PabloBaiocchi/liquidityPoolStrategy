import requests
import pandas as pd

#symbols must be followed by a 'USDT'. for example: BTCUSDT

def requestHistory(symbol,interval,startDate):
    base_url='https://api.binance.com'
    endpoint='/api/v3/klines'
    params={
        'symbol': symbol,
        'interval': interval,
        'startTime': int(startDate.strftime('%s'))*1000,
        'limit':1000
    }
    res=requests.get(base_url+endpoint,params=params)
    return res.json()

def fullHistoryDirty(symbol):
    startDate=pd.Timestamp(2017,1,1)
    df=None
    while startDate<pd.Timestamp.now():
        response=requestHistory(symbol,'1d',startDate)
        _df=pd.DataFrame(response)
        if df is None:
            df=_df
        else:
            df=pd.concat([df,_df])
        startDate=startDate+pd.Timedelta(days=1000)
    return df

def cleanDf(_df,symbol):
    df=_df.drop_duplicates()
    df=df[[6,4]].copy()
    df.columns=['timestamp',symbol]
    df['date']=df.timestamp.apply(lambda t: pd.Timestamp.fromtimestamp(t/1000).date())
    df[symbol]=df[symbol].astype(float)
    return df[['date',symbol]].copy()

def getHistory(symbol):
    df=fullHistoryDirty(symbol)
    return cleanDf(df,symbol)

def getHistorySet(symbolList):
    df=None
    for symbol in symbolList:
        _df=getHistory(symbol)
        if df is None:
            df=_df
        else:
            df=df.merge(_df,on='date')
    return df