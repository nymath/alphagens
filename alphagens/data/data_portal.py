# import pandas as pd
# import numpy as np

# class DataPortal:
#     def __init__(self):
#         start_date = Context.START_DATE
#         end_date = Context.END_DATE
#         self._all_basic_data: pd.DataFrame = joblib.load(f"{Context.DATA_PATH}/tushare.ex_basic")
#         self.prices: pd.DataFrame = self._all_basic_data["close"].unstack().fillna(method='ffill')
#         self.universe: list[str] = Index.components(ts_code=Context.BENCHMARK, end_date="20180101").index
#         self.universe = sorted([x[:-3] for x in self.universe])
    
#         self.factors: pd.DataFrame = joblib.load(f"{Context.DATA_PATH}/uqer.factor").loc[Context.trade_dates]
#         self.industry_map: pd.Series = joblib.load(f"{Context.DATA_PATH}/uqer.industry_map")
#         self.benchmark: pd.Series = Index.history(["000300.SH"], start_date, end_date)[0]["close"]

#     def history(self, date, symbols: list, field: str, lookback: int = None):
#         if lookback is not None:
#             slice_dates = DEFAULT_CALENDAR.history(date, lookback)
#             return self._all_basic_data.loc[(slice_dates, symbols), field]

#     def query_covariance(self, date, symbols, lookback):
#         """请注意协方差矩阵的数量级!!!
#         """
#         if lookback < 2 * len(symbols):
#             raise ValueError("lookback must be twice as long as length of symbols")
#         slice_data = self.history(date, symbols, "pct_chg", lookback) / 100
#         slice_data = slice_data.unstack().fillna(0)
#         mean = slice_data.mean(axis=0)
#         cov = slice_data.cov()
#         return mean, cov
    
#     @property
#     def factor_names(self):
#         return self.factors.columns.to_list()
    
#     def factor_get(self, factor_name, dates=None):
#         assert factor_name in self.factor_names
#         if dates is not None:
#             return self.factors.loc[(dates, slice(None)), factor_name]
#         else:
#             return self.factors[factor_name]
        
#     def get_trading_constraints(self, type: typing.Literal["limit_up", "limit_down"]):
#         if type == "limit_up":
#             return (self._all_basic_data["pct_chg"] >= 10).unstack().fillna(False)
# data_portal = DataPortal()