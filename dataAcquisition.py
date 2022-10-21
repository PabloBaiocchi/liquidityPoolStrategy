import requests
import pandas as pd

from query import Query

uniswap_endpoint='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'

def getStablePools(min_tvl):
    q=Query('./queries/stable_pair_pools')
    response=requests.post(uniswap_endpoint,json={'query':q.getQuery({'__tvl__':10000000})})
    if response.status_code!=200:
        print(f'Request error. code: {response.status_code}')
        return 
    data=response.json()
    return pd.DataFrame([cleanPoolResponse(pool) for pool in data['data']['pools']])

def getPoolHistory(pool_id):
    q=Query('./queries/pool_by_id')
    response=requests.post(uniswap_endpoint,json={'query':q.getQuery({'__id__':pool_id})})
    if response.status_code!=200:
        print(f'Request error. code: {response.status_code}')
        return 
    data=response.json()
    df=pd.DataFrame(data['data']['pools'][0]['poolDayData'])
    df['date']=df.date.apply(lambda d: pd.Timestamp(ts_input=d,unit='s'))
    df['tvlUSD']=df.tvlUSD.astype(float)
    df['volumeUSD']=df.volumeUSD.astype(float)
    df['feesUSD']=df.feesUSD.astype(float)
    return df

def cleanPoolResponse(raw):
    return {
        'token0':raw['token0']['symbol'],
        'token1':raw['token1']['symbol'],
        'tvl_usd':float(raw['totalValueLockedUSD']),
        'pool_id':raw['id']
    }