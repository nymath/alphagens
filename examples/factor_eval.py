import pandas as pd
import numpy as np
from alphagens.factor_utils import get_clean_factor_and_forward_returns
from alphagens.data_source.tushare import pro, Stock, Index
from alphagens.utils.calendars import DEFAULT_CALENDAR
from alphagens.backtest import QuickFactorTestor
import joblib
import argparse

parser = argparse.ArgumentParser(description="Quick Factor Testor")
parser.add_argument("-f", "--factor", type=str, default="PE", help="valid name of a factor")
parser.add_argument("-v", "--verbose", action="store_true", default=False, help="print verbose output")

ARGS = parser.parse_args()


class DataPortal:
    DATA_PATH = "./data"
    print(f"loading datas from {DATA_PATH} ...")

    universe = Index.components(ts_code="000300.SH", end_date="20180101").index
    universe = [x[:-3] for x in universe]
    all_basic_data = joblib.load(f"{DATA_PATH}/tushare.ex_basic")
    prices = all_basic_data["close"].unstack().fillna(method='ffill')
    all_factor_data = joblib.load(f"{DATA_PATH}/uqer.factor")
    industry_map = joblib.load(f"{DATA_PATH}/uqer.industry_map")

    print("==========success============")

class Context:
    FACTOR_NAME = ARGS.factor
    START_DATE = "20100101"
    END_DATE = "20180101"

    train_slice = slice("20100101", "20141231")
    valid_slice = slice("20150101", "20171231")
    train_valid_slice = slice(START_DATE, END_DATE)


    commissions = None
    rebalance_freq = "Monthly"
    refresh_days = [-1]


factor_data = DataPortal.all_factor_data[Context.FACTOR_NAME].loc[Context.train_valid_slice]

cleaned_factor = get_clean_factor_and_forward_returns(
    factor_data,
    DataPortal.prices,
)

model = QuickFactorTestor(Context.START_DATE, Context.END_DATE, DataPortal.prices)
rewards = model.evaluate(cleaned_factor, type="long_and_short", rebalance_freq=Context.rebalance_freq, days=Context.rebalance_freq)
print("the sharpe ratio of long-short portfolio is")
print(np.sqrt(252) * np.mean(rewards) / np.std(rewards))
