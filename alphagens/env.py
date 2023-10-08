import numpy as np
from .types import NO_ACTION
from .frame import DataIter
from typing import TypeVar, Tuple
from abc import ABC, ABCMeta, abstractmethod
from collections import deque
import pandas as pd

ActType = TypeVar("ActType")
ObsType = TypeVar("ObsType")

BUFFER_SIZE = 50


class MDFIter:
    def __init__(self, data, data_list, prices):
        self.data: pd.DataFrame = data
        self.data_list = data_list
        self.prices = prices
        self.returns = prices.pct_change().fillna(0)
        self.idx = 0
        self.trade_dates = list(self.data.index.levels[0])
        self.symbols = list(self.data.index.levels[1])
        self.current_date = None
        self.current_data = None

    def next(self):
        self.current_date = self.trade_dates[self.idx]
        self.current_data = self.data_list[self.idx]
        self.idx += 1
        return self.current_data

    def reset(self):
        self.current_data = None
        self.current_date = None
        self.idx = 0

    @property
    def spot_price(self):
        return self.prices.iloc[self.idx - 1]
    
    @property
    def spot_return(self):
        return self.returns.iloc[self.idx - 1]


class StockEnv:
    def __init__(self, data: pd.DataFrame, data_list: list[pd.DataFrame], prices: pd.DataFrame):
        self._iter = MDFIter(data, data_list, prices)
        self._account = Account(self._iter)
        self._initialized = False
        self._positions = np.repeat(np.nan, len(self._iter.symbols))
        self._reward = np.nan

    def step(self, 
             action: ActType
        ) -> Tuple[ObsType, float, bool, bool, dict]:
        assert self._initialized

        if action is not NO_ACTION:
            self._positions = action

        self._account.positions_series.loc[self.now] = self._positions
        self._account.strategy_returns.loc[self.now] = self._reward

        self._iter.next()
        spot_return = self._iter.spot_return
        strategy_return = np.sum(spot_return * self._positions)
        
        self._positions *= (1 + spot_return)
        self._positions /= np.sum(self._positions)

        next_state = self._iter.current_data
        self._reward = strategy_return
        truncated = False
        terminated = False
        info = None
        return next_state, self._reward, truncated, terminated, info
    
    def _update_positions(self):
        pass

    @property
    def current_date(self):
        return self._iter.current_date
    
    @property
    def now(self):
        return self._iter.current_date

    @property
    def current_data(self):
        return self._iter.current_data
    
    def reset(self) -> Tuple[ObsType, dict]:
        self._iter.reset()
        self._account.reset()
        self._positions = np.repeat(np.nan, len(self._iter.symbols)) 
        self._reward = np.nan

        self._iter.next()
        self._initialized = True
        return self._iter.current_data, None
    
    def spot(self, symbol=None, field=None) -> ObsType:
        # return self.data_iter.spot(symbol, field)
        pass


class Account:
    def __init__(self, iter: MDFIter):
        self._iter = iter
        self.positions_series = pd.DataFrame(np.nan, index=iter.trade_dates, columns=iter.symbols, dtype=np.float64)
        self.strategy_returns = pd.Series(np.nan, index=iter.trade_dates)
    
    def rebalance(self, target_positions):
        price = self._iter.spot_price()
        pre_positions = self.positions_series.loc[self._pre_trade_date]

        fees = np.nansum(np.abs(target_positions - self.positions))
        self.positions = target_positions
        self.costs = price
        return fees
    
    def reset(self):
        self.positions_series = pd.DataFrame(np.nan, index=self._iter.trade_dates, columns=self._iter.symbols, dtype=np.float64)
        self.strategy_returns = pd.Series(np.nan, index=self._iter.trade_dates) 
    
    def update(self):
        pass
        
    def calculate_capital_gains(self):
        price = self.data_iter.spot_price()
        assert np.sum(np.isnan(price)) == 0, "Detected nan value in price"
        if self.positions is None:
            return 0
        elif np.sum(self.positions) == 0:
            return 0
        else:
            capital_gains = np.nansum((price / self.costs - 1) * self.positions)
            self.positions = (price / self.costs) * self.positions
            self.positions /= np.nansum(self.positions)
            self.costs = price
            return capital_gains