import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS


# def rolling_regression(endog, exog, window: int):
#     rols = RollingOLS(endog, exog, window=window)
#     rres = rols.fit()
#     aa = rres.params.copy()
#     aa = aa.reset_index()
#     aa["asset"] = symbol
#     aa = aa.rename({"index": "date"}, axis=1)
#     aa.set_index(["date", "asset"], inplace=True)
#     return aa