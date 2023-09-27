import numpy as np
import pandas as pd
# import torchqtm.op.functional as F
from typing import Optional
import matplotlib.pyplot as plt


class RiskEvaluator(object):
    def __init__(self,
                 returns: pd.Series,
                 weights: pd.DataFrame = None,
                 freq=None,
                 rfr=0,
                 benchmark=None):
        self.returns = returns
        self.weights = weights
        self.freq = freq
        self.rfr = rfr
        self.benchmark = benchmark
        self.perf = {}

    @property
    def sharpe(self):
        return sharpe(self.returns, self.freq, self.rfr)

    @property
    def mdd(self):
        series, val, longest_time = drawdown(self.returns)
        return series, val, longest_time
    
    def _monthly_returns(self):
        pass

    def _yearly_returns(self):
        pass

    def _annualized_mean(self):
        pass

    def _annualized_volatility(self):
        pass


# def ic(factor_scores: pd.DataFrame, forward_returns: pd.DataFrame, method='pearson') -> pd.Series:
#     """
#     :return: id series
#     """
#     assert factor_scores.shape == forward_returns.shape
#     rlt = F.cs_corr(factor_scores, forward_returns, method=method)
#     rlt.fillna(0, inplace=True)
#     return rlt


def drawdown(returns: pd.Series) -> (pd.Series, float, int):
    """
    :returns : drawdown series, max drawdown, longest drawdown
    """
    net_curve = (1+returns).cumprod()
    cmax = net_curve.cummax()
    rlt = net_curve / cmax - 1
    longest_drawdown = cmax.value_counts().max() - 1
    # if isinstance(returns, pd.Series):
    #     rlt = pd.Series(rlt, index=returns.index)
    # elif isinstance(returns, np.ndarray):
    #     rlt = np.array(rlt)
    return rlt, rlt.min(), longest_drawdown


def turnover(weights: pd.DataFrame) -> pd.Series:
    """
    calculate the amount traded at each rebalance rawdata as fraction of portfolio size.
    """
    weights.fillna(0, inplace=True)
    forward_weights = weights.shift(1)
    forward_weights.fillna(0, inplace=True)
    rlt = (weights - forward_weights).abs().sum(axis=1)
    return rlt


def sharpe(returns, annulized_factor=252, rfr=0):
    if returns.isna().sum() > 0:
        raise ValueError('period_returns contains nan values.')

    mean = returns.mean()
    std = returns.std()
    _annf = annulized_factor
    return mean / std * _annf ** 0.5


def calculate_drawdowns(strategy_returns):
    net_series = np.cumprod(strategy_returns + 1)

    highwater_mark = 1
    max_drawdown = 0
    drawdown_start = False  
    max_drawdown_duration = 0
    current_duration = 0 
    
    for value in net_series:
        
        if value > highwater_mark:
            highwater_mark = value
            
            if drawdown_start:
                if current_duration > max_drawdown_duration:
                    max_drawdown_duration = current_duration

                current_duration = 0
                drawdown_start = False
        else:
            drawdown_start = True
            current_duration += 1
            
        drawdown = (highwater_mark - value) / highwater_mark
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    if current_duration > max_drawdown_duration:
        max_drawdown_duration = current_duration
        
    return max_drawdown, max_drawdown_duration


def reg_stats(strategy_return, benchmark_return, rf_return=0, annulize_factor=252):
    y = strategy_return - rf_return
    X = benchmark_return.reshape(-1, 1) - rf_return
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(X, y)
    annulized_alpha = model.intercept_ * annulize_factor
    beta = model.coef_[0]
    residuals = y - model.predict(X)
    annulized_residual_std = np.std(residuals) * np.sqrt(annulize_factor)
    
    return annulized_alpha, beta, annulized_residual_std