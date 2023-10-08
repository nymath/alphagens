raise DeprecationWarning("the frame class is deprecated and will be removed")
import pickle
from typing import Any
import numpy as np
import pandas as pd
import copy
from .calendars import XSHGExchangeCalendar
import os
import itertools
import pickle

# os.path.join(os.path.dirname(__file__))

# with open(f"{os.path.dirname(__file__)}/data/data.pkl", "rb") as f:
#     trade_dates, all_symbol, all_datas = pickle.load(f)

def backward_match(data, match):
    return np.searchsorted(data, match, "left")

def forward_match(data, match):
    return np.searchsorted(data, match, "right") - 1

NO_ACTION = frozenset("NO_ACTION")


# class DataPortal:
#     def __init__(self, trade_dates=None, symbols=None, fields=None, data=None):
#         self._times = trade_dates
#         self._symbols = np.array(all_symbol)
#         self._fields = ["open", "close"]

#         self._hash_times = pd.Series(range(len(self._times)), index=self._times)
#         self._hash_symbols = pd.Series(range(len(self._symbols)), index=self._symbols)
#         self._hash_fields = pd.Series(range(len(self._fields)), index=self._fields)

#         self._values = all_datas
#         self._values.flags.writeable = False  # read only values

#     def get_data_at_date(self, date, deep_copy=False):
#         idx = self._times.searchsorted(date, side='right') - 1
#         if not deep_copy:
#             return self._values[idx], self._times[idx]
#         else:
#             return copy.deepcopy(self._values[idx]), self._times[idx]
         
#     def get_data_at_symbol(self, symbol, deep_copy=False):
#         idx = self._symbols.searchsorted(symbol)
#         return self._values[:, idx, :]
    
#     def get_data_at_field(self, field, deep_copy=False):
#         idx = self._fields.index(field)
#         return self._values[:, :, idx]
    
#     def history(self, date, bar_count, symbols):
#         idx = self._times.searchsorted(date, side='right') - 1
#         return self._values[idx-bar_count+1: idx+1][:, self._hash_symbols[symbols], :]
    
#     def hash_history(self, date, bar_count=1):
#         return self._values[self._hash_times[date]]

#     def create_subenv(self, trade_dates: list, symbols: list, fileds: list):
#         ret_times = self._hash_times[trade_dates]
#         ret_symbols = self._hash_symbols[symbols]
#         ret_fields = self._hash_fields[fileds]
        
#         return self._values[ret_times.values, :, :][:, ret_symbols.values, :][:,:, ret_fields], ret_times.index, ret_symbols.index, ret_fields.index


class BaseFrame:
    
    def history(self, data, bar_count):
        pass

class NDFrame:
    def __init__(self, data, times, symbols, fields):
        self._values = data
        self._times = list(times)
        self._symbols = symbols
        self._fields = fields

        self._hash_times = pd.Series(range(len(self._times)), index=self._times)
        self._hash_symbols = pd.Series(range(len(self._symbols)), index=self._symbols)
        self._hash_fields = pd.Series(range(len(self._fields)), index=self._fields)
        self._values.flags.writeable = False  # read only values

    def history(self, date, bar_acount=1):
        pass

    def __len__(self):
        return len(self._values)

    def fillna(self):
        pass
    
    def save(self, file):
        with open(file, "wb") as f:
            pickle.dump(self, f)

    @property
    def symbols(self):
        return self._symbols
    
    @property
    def trade_dates(self):
        return self._times

    @property
    def fields(self):
        return self._fields

    @classmethod
    def load(cls, file) -> "NDFrame":
        with open(file, "rb") as f:
            ndf = pickle.load(f)
        return ndf
    
    def drop_to_DataFrame(self, field):
        data = self._values[:,:,self._hash_fields[field]]
        return pd.DataFrame(data=data, index=self._times, columns=self._symbols)
    

class DataIter:
    def __init__(self, data: NDFrame):
        self.data = data
        self.current_idx = 0
    
    def reset(self):
        self.current_idx = 0

    def next(self):
        self.current_idx += 1
        if self.current_idx > len(self.data) - 2:
            raise StopIteration
        
    def spot_price(self, symbol=None):
        return self.data._values[self.current_idx, :, self.data._hash_fields["close"]] 

    @property
    def current_data(self):
        return self.data._values[self.current_idx]

    @property
    def current_date(self):
        return self.data._times[self.current_idx]

# class DataIter:
#     def __init__(self, start_date, end_date, data_portal: DataPortal):
#         self.start_date = start_date
#         self.end_date = end_date
#         # self.trade_dates = trade_dates
#         self.true_index = 0
#         self.current_index = 0
#         self.end_index = forward_match(self.trade_dates, end_date)
#         # self.dirty = True
#         self.data_portal = data_portal
#         self.reset(start_date)
    
#     def reset(self, date):
#         self.date = date
#         self.current_index = 0
#         self.true_index = backward_match(self.trade_dates, date)

#     def iter(self):
#         return self

#     def next(self):
#         self.true_index += 1
#         self.current_index += 1
#         if self.true_index > self.end_index:
#             self.true_index -= 1
#             self.current_index -= 1
#             raise StopIteration
    
#     def spot(self, symbol=None, field=None):
#         return self.data_portal._values[self.true_index]
    
#     def spot_price(self, symbol=None):
#         return self.data_portal._values[self.true_index, :, self.data_portal._hash_fields["close"]] 

#     @property
#     def current_data(self):
#         return self.data_portal._values[self.true_index]

#     @property
#     def current_date(self):
#         return self.trade_dates[self.true_index]