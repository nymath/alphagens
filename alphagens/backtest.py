import pandas as pd
import numpy as np
import math
from .calendars import DEFAULT_CALENDAR
from typing import Iterable, Literal


class QuickFactorTestor:
    def __init__(self, start_date, end_date, prices):
        self.universe = list(prices.columns)
        self.n_assets = len(prices.columns)
        self._model = QuickBackTestor(start_date, end_date, prices) 

    def evaluate(self, 
        cleaned_factor: pd.DataFrame, 
        type: Literal["long_and_short", "group"]="long_and_short", 
    ):
        """_summary_

        Parameters
        ----------
        """
        self._model.reset()

        if type == "long_and_short":
            target_positions = self.get_long_short_positions(cleaned_factor)
            return self._model.run_backtest(target_positions)
        elif type == "group":
            n_groups = cleaned_factor["factor_quantile"].max()
            target_positions_list = [self.get_group_positions(cleaned_factor, i+1) for i in range(n_groups)]
            return self._model.run_backtests(target_positions_list)
    
    def get_group_positions(self, cleaned_factor: pd.DataFrame, factor_quantile: int):
        tmp = cleaned_factor.query(f"factor_quantile=={factor_quantile}")["factor_quantile"].unstack().reindex(self.universe, axis=1)
        # tmp = cleaned_factor[cleaned_factor['factor_quantile'] == factor_quantile]["factor_quantile"].unstack().reindex(self.universe, axis=1)
        weights = (tmp > 0) / np.repeat((tmp > 0).sum(axis=1).values.reshape(-1, 1), self.n_assets, axis=1)
        return weights

    def get_long_short_positions(self, cleaned_factor: pd.DataFrame):
        max_quantile = cleaned_factor["factor_quantile"].max()
        min_quantile = cleaned_factor["factor_quantile"].min()
        long_positions = self.get_group_positions(cleaned_factor, max_quantile)
        short_positions = self.get_group_positions(cleaned_factor, min_quantile)
        return long_positions - short_positions

    def summary(self):
        pass


class QuickBackTestor:
    def __init__(self, start_date, end_date, prices):
        self.start_date = start_date
        self.end_date = end_date
        self._prices = prices
        self._returns = self._prices.pct_change().fillna(0)
        self._commission = None
        self._trade_dates = DEFAULT_CALENDAR.sessions_in_range(self.start_date, self.end_date)
        self._results = {"strategy_rewards": None}
 
    def run_backtest(self, strategy: pd.DataFrame):
        if not set(strategy.loc[self.start_date:self.end_date].index).issubset(set(self._trade_dates)):
            raise ValueError("the index of strategy must be a trade date")
        
        if strategy.isna().sum().sum() > 0:
            raise ValueError("the elements of startegy should not be nan")
        
        strategy = strategy.loc[self.start_date:self.end_date]
        rebalance_dates = strategy.index.to_list()
        dates = list(zip(rebalance_dates[:-1], rebalance_dates[1:]))
        results = []
        for start_date, end_date in dates:
            result = self._rewards_in_range(strategy.loc[start_date], start_date, end_date)
            results.append(result)
        self._results["strategy_rewards"] = pd.concat(results).reindex(self._trade_dates).fillna(0)
        return self._results["strategy_rewards"]
    
    def run_backtests(self, strategies: Iterable[pd.DataFrame]):
        """run multiple backtests
        The strategies should be aligned in the same format

        Parameters
        ----------
        strategies : Iterable[pd.DataFrame]
            _description_
        """
        sample_strategy = strategies[0]
        if not set(sample_strategy.index).issubset(set(self._trade_dates)):
            raise ValueError("the index of strategy must be a trade date")
        
        if sample_strategy.isna().sum().sum() > 0:
            raise ValueError("the elements of startegy should not be nan")
        
        rebalance_dates = sample_strategy.index.to_list()
        dates = list(zip(rebalance_dates[:-1], rebalance_dates[1:]))
        results = [] 
        for start_date, end_date in dates:
            current_strategy = pd.concat([strategy.loc[start_date] for strategy in strategies], axis=1, ignore_index=True)
            result = self._rewards_in_range(current_strategy, start_date, end_date)
            results.append(result)
        self._results["strategy_rewards"] = pd.concat(results).reindex(self._trade_dates).fillna(0)  
        return self._results["strategy_rewards"]

    def reset(self):
        self._results = {"strategy_rewards": None}

    def summary(self):
        pass

    def _rewards_in_range(self, start_position, start_date, end_date):
        returns_slice = self._returns.loc[start_date:end_date].copy(deep=True)
        # construct the imaginary returns:
        # short a stock is equal to long the stock that is purely negatively correlated with the prime stock
        returns_slice.iloc[:, np.where(start_position < 0)[0]] *= -1 
        start_position = np.abs(start_position)
        returns_slice.iloc[0] = 0
        pnls = (returns_slice + 1).cumprod()
        pnl = pnls.dot(start_position)
        rewards = pnl.pct_change()
        return rewards.iloc[1:]
    

class SlowBackTestor:
    def __init__(self, start_date, end_date, prices):
        self.start_date = start_date
        self.end_date = end_date
        self._prices = prices
        self._returns = self._prices.pct_change().fillna(0)
        self._commission = None
        self._trade_dates = DEFAULT_CALENDAR.sessions_in_range(self.start_date, self.end_date)
        self._results = {"strategy_rewards": None}
 
    def run_backtest(self, strategy: pd.DataFrame):
        if not set(strategy.loc[self.start_date:self.end_date].index).issubset(set(self._trade_dates)):
            raise ValueError("the index of strategy must be a trade date")
        
        if strategy.isna().sum().sum() > 0:
            raise ValueError("the elements of startegy should not be nan")
        
        strategy = strategy.loc[self.start_date:self.end_date]
        rebalance_dates = strategy.index.to_list()
        dates = list(zip(rebalance_dates[:-1], rebalance_dates[1:]))
        results = []
        for start_date, end_date in dates:
            target_position = strategy.loc[start_date]
            # masking stocks that can not be traded
            result = self._rewards_in_range(target_position, start_date, end_date)
            results.append(result)
        self._results["strategy_rewards"] = pd.concat(results).reindex(self._trade_dates).fillna(0)
        return self._results["strategy_rewards"]
    
    def run_backtests(self, strategies: Iterable[pd.DataFrame]):
        """run multiple backtests
        The strategies should be aligned in the same format

        Parameters
        ----------
        strategies : Iterable[pd.DataFrame]
            _description_
        """
        sample_strategy = strategies[0]
        if not set(sample_strategy.index).issubset(set(self._trade_dates)):
            raise ValueError("the index of strategy must be a trade date")
        
        if sample_strategy.isna().sum().sum() > 0:
            raise ValueError("the elements of startegy should not be nan")
        
        rebalance_dates = sample_strategy.index.to_list()
        dates = list(zip(rebalance_dates[:-1], rebalance_dates[1:]))
        results = [] 
        for start_date, end_date in dates:
            current_strategy = pd.concat([strategy.loc[start_date] for strategy in strategies], axis=1, ignore_index=True)
            result = self._rewards_in_range(current_strategy, start_date, end_date)
            results.append(result)
        self._results["strategy_rewards"] = pd.concat(results).reindex(self._trade_dates).fillna(0)  
        return self._results["strategy_rewards"]

    def reset(self):
        self._results = {"strategy_rewards": None}

    def summary(self):
        pass

    def _rewards_in_range(self, start_position, start_date, end_date):
        returns_slice = self._returns.loc[start_date:end_date].copy(deep=True)
        # construct the imaginary returns:
        # short a stock is equal to long the stock that is purely negatively correlated with the prime stock
        returns_slice.iloc[:, np.where(start_position < 0)[0]] *= -1 
        start_position = np.abs(start_position)
        returns_slice.iloc[0] = 0
        pnls = (returns_slice + 1).cumprod()
        pnl = pnls.dot(start_position)
        rewards = pnl.pct_change()
        return rewards.iloc[1:]