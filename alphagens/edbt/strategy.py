import tqdm
import pandas as pd
from .engine import SimulationEngine
from .broker import SimulatedBroker
from .account import Account


class BaseStrategy:
    def __init__(self, engine: SimulationEngine, broker: SimulatedBroker, account: Account):
        self.broker = broker
        self._engine = engine
        self.account = account
        self.trade_dates = self._engine.trade_dates

    @property
    def current_date(self):
        return self._engine.current_date
    
    @property
    def spot_prices(self):
        return self._engine.spot_prices
    
    def order(self, positions: pd.Series):
        return self.account.order(positions)
    
    def before_trading_end(self):
        raise NotImplementedError

    def _before_trading_end(self):
        self.before_trading_end()
        self.broker.parser_order(self.account)

    def run_backtest(self):
        with tqdm.tqdm(total=len(self.trade_dates), desc="") as pbar:
            while True:
                try:
                    self._engine.on_session_start()
                    self._before_trading_end()
                    self.account.on_session_end()
                except StopIteration:
                    break
                finally:
                    pbar.update(1)