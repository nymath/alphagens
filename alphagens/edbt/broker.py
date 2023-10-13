import pandas as pd
from .engine import SimulationEngine
from .account import Account

class SimulatedBroker:
    def __init__(self, engine: SimulationEngine):
        self._engine = engine
        self.limit_up = self._engine._data_portal.get_trading_constraints("limit_up")

    def trading_constraints(self):
        pass

    def parser_order(self, account: Account):
        try:
            nums = account._order_lists.pop()
            prices = self._engine.spot_prices.loc[nums.index] # 可以加入冲击模型得到fill_price

            constraints = self.limit_up.loc[self._engine.current_date]
            constraints = constraints[constraints]

            sell_orders = nums[nums < 0].index
            buy_orders = nums[nums > 0].index
            buy_orders_masked = buy_orders.intersection(constraints)

            nums[buy_orders_masked] = 0

            filled_orders = pd.concat([nums, prices], axis=1)
            filled_orders.columns = ["nums", "fill_price"]
            account._filled_order_lists.append(filled_orders)
            
        except IndexError:
            pass
