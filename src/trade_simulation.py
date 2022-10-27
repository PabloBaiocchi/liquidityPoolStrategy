import pandas as pd
import scipy.stats as stats
import numpy as np

def run_iteration(day_projection,p_value,env):
    start_index=int(len(env)/3)
    current_capital=1000000
    unclaimed_fees=0

    log_rows=[]

    for index,row in env.iloc[start_index:].iterrows():

        unclaimed_fees=unclaimed_fees+row.returns*current_capital

        history=pool.iloc[:index].returns
        sample=history.sort_values(ascending=True).iloc[:int(len(history)*.99)]
        
        fit=stats.skewnorm.fit(sample)
        conf_low,conf_high=stats.skewnorm.interval(a=fit[0],loc=fit[1],scale=fit[2],confidence=1-2*p_value)
        projected_fees=conf_low*day_projection*unclaimed_fees

        log_rows.append({
            'date':row.date,
            'current_capital':current_capital,
            'unclaimed_fees':unclaimed_fees,
            'projected_fees':projected_fees,
            'reinvest_cost':row.reinvest
        })

        if projected_fees>row.reinvest and unclaimed_fees>row.reinvest:
            current_capital=current_capital+unclaimed_fees-row.reinvest
            unclaimed_fees=0

    results=pd.DataFrame(log_rows)
    results['p_value']=p_value
    results['day_projection']=day_projection
    return results

def run(file_location):
    df=None
    for p_val in np.linspace(.02,.2,10):
        for days in np.linspace(7,49,7,dtype=int):
            print(f'Simulating. p value: {p_val} , days: {days}')
            results=run(days,p_val)
            if df is None:
                df=results
            else:
                df=pd.concat([df,results]).reset_index(drop=True)
            df.to_csv(file_location,index=False)