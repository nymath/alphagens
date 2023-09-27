from concurrent.futures import ThreadPoolExecutor
import tushare as ts
import pandas as pd
from joblib import Parallel, delayed, Memory
from ..calendars import XSHGExchangeCalendar

ts.set_token("4701ef6fe54d814aad7ec2ec77a62c9152a9c3521bde0626c9717470")
pro = ts.pro_api()

CALENDAR = XSHGExchangeCalendar()
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

def ex_stock_history(symbols, start_date, end_date):

    def worker(symbol):
        return ex_get_one_stock(symbol, start_date, end_date)
    
    results = Parallel(n_jobs=50, prefer="threads")(delayed(worker)(symbol) for symbol in symbols)
    return results

def stock_history(symbols, start_date, end_date):

    def worker(symbol):
        return get_one_stock(symbol, start_date, end_date)
    
    results = Parallel(n_jobs=50, prefer="threads")(delayed(worker)(symbol) for symbol in symbols)
    return results

@memory.cache
def get_one_index(ts_code, start_date, end_date):
    df = pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df['trade_date'] = pd.DatetimeIndex(df['trade_date'])
    df.sort_values("trade_date", inplace=True)
    df.set_index("trade_date", inplace=True)
    df = df.reindex(CALENDAR.sessions_in_range(start_date, end_date))
    return df


def index_history(symbols, start_date, end_date):
    results = []

    def worker(symbol):
        return get_one_index(symbol, start_date, end_date)
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(worker, symbol) for symbol in symbols]
        
        for future in futures:
            results.append(future.result()) 
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
    df = df.reindex(CALENDAR.sessions_in_range(start_date, end_date))
    return df


if __name__ == "__main__":
    ex_get_one_stock("000001.SZ", "20100101", "20150101")