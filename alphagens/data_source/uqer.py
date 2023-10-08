# -*- coding: utf-8 -*-
from alphagens.data_source._dataapi_linux36 import Client
import pandas as pd
from io import StringIO

TOKEN = "8d08961ec3c2ff4f22b627f976ed1583d792247526e6cde96e98d8cdd645a259"

def split_date_range(start_date, end_date, n_splits):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    total_days = (end_date - start_date).days
    days_per_split = total_days // n_splits
    
    date_ranges = []
    current_start = start_date
    for _ in range(n_splits - 1):
        current_end = current_start + timedelta(days=days_per_split - 1)
        date_ranges.append((current_start.strftime('%Y%m%d'), current_end.strftime('%Y%m%d')))
        current_start = current_end + timedelta(days=1)
    date_ranges.append((current_start.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')))
    
    return date_ranges
			

def EquIndustryGet(secID="",ticker=["688005", "600001"], industryVersionCD="010303", into_date="", industry="", industryID="", industryID1=""):
	try:
		client = Client()
		client.init(TOKEN)
		url2=f'/api/equity/getEquIndustry.csv?\
field=&industryVersionCD={industryVersionCD}\
&industry=\
&secID=\
&ticker={",".join(ticker)}\
&intoDate={into_date}\
&industryID1=\
&industryID2=\
&industryID3=\
&equTypeID=\
&industryID='
		code, result = client.getData(url2)
		if(code==200):
			data = result.decode("gbk")
			df = pd.read_csv(StringIO(data))
			return df
		else:
			print (code)
			print (result)
	except Exception as e:
		raise e


def MktStockFactorsOneDayProGet(trade_date="20170612",secID="",ticker=["000001", "600000"], field=["STOM"],pandas="1"):
	try:
		client = Client()
		client.init(TOKEN)
		url2=f'/api/market/getMktStockFactorsOneDayPro.csv?\
field={",".join(field)}&\
secID=&\
ticker={",".join(ticker)}&\
tradeDate={trade_date}'
		code, result = client.getData(url2)
		if(code==200):
			data = result.decode("gbk")
			df = pd.read_csv(StringIO(data))
			return df
		else:
			print (code)
			print (result)
	except Exception as e:
		raise e


def MktStockFactorsOneDayGet(trade_date="20150227",secID="",ticker=["000001","600000"], field="",pandas="1"):
	try:
		client = Client()
		client.init(TOKEN)
		url2=f'/api/market/getStockFactorsOneDay.csv?\
field=&\
secID=&\
ticker={",".join(ticker)}&\
tradeDate={trade_date}'

		code, result = client.getData(url2)
		if(code==200):
			data = result.decode("gbk")
			df = pd.read_csv(StringIO(data))
			return df
		else:
			print (code)
			print (result)
	except Exception as e:
		raise e


def MktStockFactorsDateRangeGet(secID="", ticker=["000001", "000002"], start_date="20170612", end_date="20170616", field=[], pandas="1"):
	try:
		client = Client()
		client.init(TOKEN)
		url2=f'/api/market/getStockFactorsDateRange.csv?\
field=&\
secID=&\
ticker={",".join(ticker)}&\
beginDate={start_date}&\
endDate={end_date}'

		code, result = client.getData(url2)
		if(code==200):
			data = result.decode("gbk")
			df = pd.read_csv(StringIO(data))
			return df
		else:
			print (code)
			print (result)
	except Exception as e:
		raise e


# def P_MktStockFactorsDateRangeGet(secID="", ticker=["000001", "000002"], start_date="20170612", end_date="20170616", field=[], pandas="1", n_jobs=4, n_splits=8):
# 	inputs = None
# date_ranges = split_date_range(start_date, end_date, n_splits)	
#     results = Parallel(n_jobs=n_jobs)(
#         delayed(MktStockFactorsDateRangeGet)(secID="", ticker=ticker, start_date=s_date, end_date=e_date, field=field, pandas="1")
#         for s_date, e_date in date_ranges
#     )
# 	return results


if __name__ == '__main__':
	EquIndustryGet(ticker=["000001", "000002"])