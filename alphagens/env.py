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
        self.current_date = None
        self.current_data = None

    def next(self):
        self.current_date = self.data.index.levels[0][self.idx]
        self.current_data = self.data_list[self.idx]
        self.idx += 1
        return self.current_data

    @property
    def spot_price(self):
        return self.prices.iloc[self.idx - 1]
    
    @property
    def spot_return(self):
        return self.returns.iloc[self.idx - 1]


class StockEnv:
    def __init__(self, data: pd.DataFrame, data_list: list[pd.DataFrame], prices: pd.DataFrame):
        self._data = data
        self._data_list = data_list
        self._mdf_iter = MDFIter(data, self._data_list, prices)
        # self._account = Account(self._mdf_iter)
        self._initialized = False
        self._positions = None
        self._costs = None

    def step(self, 
             action: ActType
        ) -> Tuple[ObsType, float, bool, bool, dict]:
        assert self._initialized

        if action is not NO_ACTION:
            self._positions = action
        
        self._mdf_iter.next()
        spot_return = self._mdf_iter.spot_return
        new_positions = self._positions * (1 + spot_return)
        strategy_return = np.sum(spot_return * self._positions)
        self._positions = new_positions / np.sum(new_positions)
        next_state = self._mdf_iter.current_data

        reward = strategy_return
        truncated = False
        terminated = False
        info = None
        return next_state, reward, truncated, terminated, info
    
    def _update_positions(self):
        pass

    @property
    def current_date(self):
        return self._mdf_iter.current_date

    @property
    def current_data(self):
        return self._mdf_iter.current_data
    
    def reset(self) -> Tuple[ObsType, dict]:
        self._mdf_iter.next()
        self._initialized = True
        return self._mdf_iter.current_data, None
    
    def spot(self, symbol=None, field=None) -> ObsType:
        # return self.data_iter.spot(symbol, field)
        pass


class Account:
    def __init__(self, data_iter: DataIter):
        self.data_iter = data_iter
        self.positions = np.repeat(0, len(data_iter.data._symbols))
        self.costs = None
    
    def rebalance(self, target_positions):
        price = self.data_iter.spot_price()
        if self.positions is NO_ACTION:
            fees = np.nansum(np.abs(target_positions)) 
        else:
            fees = np.nansum(np.abs(target_positions - self.positions))
        self.positions = target_positions
        self.costs = price
        return fees
    
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