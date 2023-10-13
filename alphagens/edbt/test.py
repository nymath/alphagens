import pandas as pd
import tqdm
import sys
import time


class Metric:
    def __init__(self):
        pass

    def after_session_end():
        pass

class SimulationEngine:
    """模拟市场
    """
    def __init__(self, trade_dates, data_portal: DataPortal):
        self._trade_dates = trade_dates
        self.data_portal = data_portal
        self.iter = iter(trade_dates)
        self.current_date = None
        self.spot_prices = None
    
    def on_session_start(self):
        self._next()

    def _next(self):
        self.current_date = next(self.iter)
        self.spot_prices = self.data_portal.prices.loc[self.current_date] # 索引改进, 目前会消耗200ms

class SimulatedBroker:
    def __init__(self, engine: SimulationEngine):
        self._engine = engine
        self.limit_up = self._engine.data_portal.get_trading_constraints("limit_up")

    def trading_constraints(self):
        pass

    def parser_order(self, account: "Account"):
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

class Account:
    """统计账户信息
    """
    def __init__(self, engine):
        self._engine = engine
        self.positions = pd.Series(0, index=data_portal.universe, dtype=int)
        self.cash = 100000000
        self._dirty = True
        self._order_lists = []
        self._filled_order_lists = []

    @property
    def current_date(self):
        return self._engine.current_date

    @property
    def spot_prices(self):
        return self._engine.spot_prices

    def _update(self):
        self._dirty = True
        try:
            filled_orders = self._filled_order_lists.pop()
            assets = filled_orders.index
            nums = filled_orders["nums"]
            fill_price = filled_orders["fill_price"]
            total_cost = (nums * fill_price).sum() # 还可以加入成本, 印花税
            self.cash -= total_cost
            self.positions[assets] += nums
        except IndexError:
            pass
    
    def on_session_start(self):
        pass
        # self._previous_total_returns = self.returns

    def on_session_end(self):
        self._update()

    def order(self, amounts: pd.Series):
        self._order_lists.append(amounts)

    def order_target_pct_to(self, target_weights: pd.Series):
        assert target_weights.sum() <= 1.001
        assets = target_weights.index
        portfolio_value = self.portfolio_value
        spot_prices = self._engine.spot_prices.loc[assets]
        nums = (target_weights * portfolio_value / spot_prices).fillna(0).astype(int) - self.positions.loc[assets]
        self.order(nums)

    @property
    def portfolio_value(self):
        return self.cash + (self.positions * self.spot_prices).sum()
    
    @property
    def current_portfolio_weight(self):
        pass

class BaseStrategy:
    def __init__(self, engine, broker, account):
        self.broker: SimulatedBroker = broker
        self.engine: SimulationEngine = engine
        self.account: Account = account

    @property
    def current_date(self):
        return self.engine.current_date
    
    @property
    def spot_prices(self):
        return self.engine.spot_prices
    
    def order(self, positions: pd.Series):
        return self.account.order(positions)
    
    def before_trading_end(self):
        raise NotImplementedError

    def _before_trading_end(self):
        self.before_trading_end()
        self.broker.parser_order(self.account)

    def run_backtest(self):
        with tqdm.tqdm(total=len(Context.trade_dates), desc="") as pbar:
            while True:
                try:
                    self.engine.on_session_start()
                    self._before_trading_end()
                    self.account.on_session_end()
                except StopIteration:
                    break
                finally:
                    pbar.update(1)

class BuyAndHold(BaseStrategy):
    def __init__(self, engine, broker, account):
        super().__init__(engine, broker, account)
    
    def before_trading_end(self):
        if self.current_date == Context.trade_dates[0]:
            self.account.order_target_pct_to(pd.Series(1, index=["000001"]))

engine = SimulationEngine(Context.trade_dates, data_portal)
broker = SimulatedBroker(engine)
account = Account(engine)
algo = BuyAndHold(engine, broker, account)