from re import I
import pandas as pd
import scipy.stats as stats
import numpy as np

from src.gas import getHistorical

def getEnvironment():
    gas=getHistorical()

    pool_data=pd.read_csv('../data/pool_data.csv',parse_dates=['date'])
    start_date=pool_data[pool_data.pool_name=='USDC_USDT_01'].date.min()
    pool=pool_data[(pool_data.pool_name=='USDC_USDT_05') & (pool_data.date>=start_date)].reset_index(drop=True)

    return pool[['date','tvlUSD','feesUSD']].merge(gas[['date','reinvest']])


def get_sample(history,p_val):
    return history.sort_values(ascending=True).iloc[:int(len(history)*(1-p_val))]

def get_projected_return(sample,projection_p_value,day_count):
    fit_a,fit_loc,fit_scale=stats.skewnorm.fit(sample)
    fit_mean,fit_variance=stats.skewnorm.stats(a=fit_a,loc=fit_loc,scale=fit_scale,moments='mv')
    norm_mean=fit_mean*day_count
    norm_std=(fit_variance*day_count)**(.5)
    lower_bound,upper_bound=stats.norm.interval(1-2*projection_p_value,loc=norm_mean,scale=norm_std)
    return lower_bound

def run_iteration(day_projection,projection_p_value,fit_p_value,environment,initial_capital,test_size):
    env=environment.copy()
    start_index=int(len(env)*test_size)
    current_capital=initial_capital
    env['tvlUSD']=env.tvlUSD+initial_capital
    env['returns']=env.feesUSD/env.tvlUSD
    unclaimed_fees=0

    log_rows=[]

    for index,row in env.iloc[start_index:].iterrows():

        unclaimed_fees=unclaimed_fees+row.returns*current_capital

        history=env.iloc[:index].returns
        sample=get_sample(history,fit_p_value)
        projected_return=get_projected_return(sample,projection_p_value,day_projection)
        
        projected_fees_on_reinvest=projected_return*(unclaimed_fees-row.reinvest)

        log_rows.append({
            'date':row.date,
            'current_capital':current_capital,
            'unclaimed_fees':unclaimed_fees,
            'projected_fees_on_reinvest':projected_fees_on_reinvest,
            'reinvest_cost':row.reinvest
        })

        if projected_fees_on_reinvest>row.reinvest and unclaimed_fees>row.reinvest:
            reinvest_sum=unclaimed_fees-row.reinvest
            current_capital=current_capital+reinvest_sum
            unclaimed_fees=0

    results=pd.DataFrame(log_rows)
    results['fit_p_value']=fit_p_value
    results['projection_p_value']=projection_p_value
    results['day_projection']=day_projection
    results['test_size']=test_size
    return results

def run(p_val_range,day_range,environment,fit_p_val,initial_capital,test_size,file_location):
    df=None
    for p_val in p_val_range:
        for days in day_range:
            print(f'Simulating. p value: {p_val} , days: {days}')
            results=run_iteration(days,p_val,fit_p_val,environment,initial_capital,test_size)
            if df is None:
                df=results
            else:
                df=pd.concat([df,results]).reset_index(drop=True)
            df.to_csv(file_location,index=False)