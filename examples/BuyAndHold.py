import time
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from alphagens.calendars import XSHGExchangeCalendar
from alphagens.env import StockEnv
from alphagens.agent import BaseAgent
from alphagens.types import NO_ACTION


data = joblib.load("./data/all_data.mdf")
bt_data = joblib.load("./data/all_data.list")

prices = data["close"].unstack().fillna(method="ffill")

calendar = XSHGExchangeCalendar()
universe = list(data.index.levels[1])
trade_dates = list(data.index.levels[0])
REBALANCE_DATES = calendar.Monthly(trade_dates, [-1])


class BuyAndHold(BaseAgent):
    def __init__(self, data):
        super().__init__(data)
        self.i = -1
    
    def take_action(self, state, date):
        self.buffer.append(state)
        self.i += 1
        if self.i == 0:
            target_positions = np.array([0.2 for i in range(5)]) 
            return target_positions
        else:
            return NO_ACTION


agent = BuyAndHold(data)
env = StockEnv(data, bt_data, prices)
state, info = env.reset()
positions = []
returns = [0] 
t0 = time.time()


while True:
    try:
        print(f"current date is {env.current_date}")
        action = agent.take_action(state, env.current_date)
    
        next_state, reward, truncated, terminated, info = env.step(action)
        state = next_state
        returns.append(reward)

    except IndexError:
        break

print(time.time() - t0, "\n")
print(np.cumprod(np.array(returns) + 1)) 
