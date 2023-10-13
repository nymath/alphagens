import tushare as ts
import pandas as pd
from joblib import Parallel, delayed, Memory
from ..calendars import DEFAULT_CALENDAR

ts.set_token("4701ef6fe54d814aad7ec2ec77a62c9152a9c3521bde0626c9717470")
pro = ts.pro_api()

MAX_JOBS = 64
DEFAULT_START_DATE = "20100101"
DEFAULT_END_DATE = "20230901"

memory = Memory(".cache")


@memory.cache
def ex_get_one_stock(ts_code, start_date, end_date):
    df: pd.DataFrame = ts.pro_bar(ts_code=ts_code, adj='qfq', start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True, ignore_index=True)
    return df

@memory.cache
def get_one_stock(ts_code, start_date, end_date):
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True, ignore_index=True)
    return df

@memory.cache
def get_one_stock_daily_basic(ts_code, start_date, end_date):
    df = pro.daily_basic(**{
        "ts_code": ts_code,
        "trade_date": "",
        "start_date": start_date,
        "end_date": end_date,
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "close",
        "turnover_rate",
        "turnover_rate_f",
        "volume_ratio",
        "pe",
        "pe_ttm",
        "pb",
        "ps",
        "ps_ttm",
        "dv_ratio",
        "dv_ttm",
        "total_share",
        "float_share",
        "free_share",
        "total_mv",
        "circ_mv"
    ])
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True, ignore_index=True)
    return df


@memory.cache
def get_one_stock_moneyflow(ts_code, start_date, end_date):
    df = pro.moneyflow(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True, ignore_index=True)
    return df

@memory.cache
def get_one_stock_tech_factor(ts_code, start_date, end_date):
    df = pro.stk_factor(**{
        "ts_code": "000001.SZ",
        "start_date": "",
        "end_date": "",
        "trade_date": "",
        "limit": "",
        "offset": ""
    }, fields=[
        "ts_code",
        "trade_date",
        "close",
        "open",
        "high",
        "low",
        "pre_close",
        "change",
        "pct_change",
        "vol",
        "amount",
        "adj_factor",
        "open_hfq",
        "open_qfq",
        "close_hfq",
        "close_qfq",
        "high_hfq",
        "high_qfq",
        "low_hfq",
        "low_qfq",
        "pre_close_hfq",
        "pre_close_qfq",
        "macd_dif",
        "macd_dea",
        "macd",
        "kdj_k",
        "kdj_d",
        "kdj_j",
        "rsi_6",
        "rsi_12",
        "rsi_24",
        "boll_upper",
        "boll_mid",
        "boll_lower",
        "cci"
    ])
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True, ignore_index=True)
    return df


class Stock:
    @staticmethod
    def tech_factor(symbols, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
        def worker(symbol):
            return get_one_stock_tech_factor(symbol, start_date, end_date)
        results = Parallel(n_jobs=MAX_JOBS, prefer="threads")(delayed(worker)(symbol) for symbol in symbols)
        return results

    @staticmethod
    def moneyflow(symbols, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
        def worker(symbol):
            return get_one_stock_moneyflow(symbol, start_date, end_date)

        works_to_do = [delayed(worker)(symbol) for symbol in symbols] 
        results = Parallel(n_jobs=MAX_JOBS, prefer="threads")(works_to_do)
        return results

    @staticmethod
    def daily_basic(symbols, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
        def worker(symbol):
            return get_one_stock_daily_basic(symbol, start_date, end_date)
    
        results = Parallel(n_jobs=MAX_JOBS, prefer="threads")(delayed(worker)(symbol) for symbol in symbols)

        return results

    @staticmethod
    def ex_history(symbols, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):

        def worker(symbol):
            return ex_get_one_stock(symbol, start_date, end_date)
        
        works_to_do = [delayed(worker)(symbol) for symbol in symbols]

        results = Parallel(n_jobs=MAX_JOBS, prefer="threads")(works_to_do)

        return results

    @staticmethod
    def history(symbols, start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE):
        
        def worker(symbol):
            return get_one_stock(symbol, start_date, end_date)

        works_to_do = [delayed(worker)(symbol) for symbol in symbols] 
        
        results = Parallel(n_jobs=MAX_JOBS, prefer="threads")(works_to_do)

        return results


@memory.cache
def _get_one_index(ts_code, start_date, end_date):
    df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True)
    df.set_index("trade_date", inplace=True)
    df = df.reindex(DEFAULT_CALENDAR.sessions_in_range(start_date, end_date))
    return df


def index_history(symbols, start_date, end_date):
    def worker(symbol):
        return _get_one_index(symbol, start_date, end_date)
    
    results = Parallel(n_jobs=MAX_JOBS, prefer="threads")(delayed(worker)(symbol) for symbol in symbols)
    return results


def get_rf_ret(start_date, end_date, termination=10):
    df = pro.yc_cb(**{
        "ts_code": "",
        "curve_type": 0,
        "trade_date": "",
        "start_date": start_date,
        "end_date": end_date,
        "curve_term": 10,
        "limit": "",
        "offset": ""
    }, fields=[
        "trade_date",
        "yield",
    ])
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True)
    df.set_index("trade_date", inplace=True)
    df = df.reindex(DEFAULT_CALENDAR.sessions_in_range(start_date, end_date))
    return df


class Index:
    @staticmethod
    def components(ts_code, end_date):
        code_maps = {
            "000300.SH": "399300.SZ",
            "399300.SZ": "399300.SZ",
        }
        ts_code = code_maps[ts_code]
        df = pro.index_weight(index_code=ts_code, end_date=end_date)
        df = df.sort_values(["trade_date", "con_code"], ignore_index=True)
        date = df["trade_date"].iloc[-1]
        df = df[df["trade_date"]==date]
        return pd.Series(df["weight"].values / 100, index=df["con_code"]) 
    
    @staticmethod
    def history(symbols, start_date, end_date):
        def worker(symbol):
            return _get_one_index(symbol, start_date, end_date)
        
        results = Parallel(n_jobs=MAX_JOBS, prefer="threads")(delayed(worker)(symbol) for symbol in symbols)

        return results
    

class Bond:
    pass

