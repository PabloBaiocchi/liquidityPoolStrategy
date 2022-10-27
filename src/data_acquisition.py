import requests
import pandas as pd

from src.query import Query

uniswap_endpoint='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'

def getStablePoolHistory(min_tvl):
    stable_pools=getStablePools(min_tvl)
    df_list=[getPoolHistory(pool_id) for pool_id in stable_pools.pool_id]
    history=pd.concat(df_list).reset_index(drop=True)
    name_df=poolNames(stable_pools,history)
    return history.merge(name_df[['pool_id','pool_name']],on='pool_id')

def getStablePools(min_tvl):
    q=Query('../queries/stable_pair_pools')
    response=requests.post(uniswap_endpoint,json={'query':q.getQuery({'__tvl__':min_tvl})})
    if response.status_code!=200:
        print(f'Request error. code: {response.status_code}')
        return 
    data=response.json()
    return pd.DataFrame([cleanPoolResponse(pool) for pool in data['data']['pools']])

def getPoolHistory(pool_id):
    q=Query('../queries/pool_by_id')
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
    df['pool_id']=pool_id
    return df

def poolNames(stable_pools,history):
    fee_df=history.groupby('pool_id').apply(fees).to_frame()
    fee_df.columns=['fee']
    name_df=fee_df.merge(stable_pools[['token0','token1','pool_id']],on='pool_id')
    name_df['pool_name']=name_df.apply(lambda row: f'{row.token0}_{row.token1}_{row.fee}',axis=1)
    return name_df

def cleanPoolResponse(raw):
    return {
        'token0':raw['token0']['symbol'],
        'token1':raw['token1']['symbol'],
        'tvl_usd':float(raw['totalValueLockedUSD']),
        'pool_id':raw['id']
    }

def fees(df):
    return str(round(df.feesUSD.sum()/df.volumeUSD.sum(),5))[-2:]