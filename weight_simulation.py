import numpy as np
import random
import pandas as pd

def generateWeightsRow(n):
    v=np.array([random.random() for i in range(n)])
    return v/sum(v)

def weightMatrix(n_pools,n_reps):
    return np.matrix([generateWeightsRow(n_pools) for i in range(n_reps)])

def portfolioReturns(returnsDf,weightMatrix):
    returnsVector=np.matrix([returnsDf[col].mean() for col in returnsDf.columns]).T
    return weightMatrix*returnsVector

def run(daily_returns_df,weights):
    pools=daily_returns_df.columns
    weights_matrix=weightMatrix(len(pools),weights) if type(weights)==int else weights
    daily_returns_matrix=daily_returns_df.to_numpy()
    results_matrix=daily_returns_matrix*weights_matrix.T
    results_means=results_matrix.mean(axis=0)
    results_std=results_matrix.std(axis=0)
    full_results_matrix=np.concatenate([weights_matrix,results_means.T,results_std.T],axis=1)
    return pd.DataFrame(full_results_matrix,columns=list(pools)+['daily_return','daily_std'])