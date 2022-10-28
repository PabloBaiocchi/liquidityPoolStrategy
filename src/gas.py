import pandas as pd

import src.crypto_historical as ch

def getHistorical():
    gas=pd.read_csv('../data/avg_gas_price_historial_etherscan.csv',header=0,names=['date','unix_date','wei'],parse_dates=['date'])

    eth=ch.getHistory('ETHUSDT')
    eth['date']=eth.date.apply(lambda d: pd.Timestamp(d.year,d.month,d.day))

    gas=gas[['date','wei']].merge(eth)
    gas['gasUSDT']=gas.wei*gas.ETHUSDT/(10**18)
    gas['tx']=gas.gasUSDT*350000
    gas['reinvest']=gas.tx*2
    
    return gas