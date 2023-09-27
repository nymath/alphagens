import pandas as pd
import datetime
import typing

NO_ACTION = frozenset("NO_ACTION")

DateLike = typing.Union[pd.Timestamp, str, int, float, datetime.datetime]
