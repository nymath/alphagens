raise NotImplementedError

class Pipeline:
    def __init__(self, context):
        self.context = context
        self.trade_dates = TRADE_DATES
        self._date_iter = iter(TRADE_DATES)
        self.current_date = None
        self._results = []

    def next(self):
        self.current_date = next(self._date_iter)

    def order_pct_to(self, target_percent):
        #TODO: add type checking
        if target_percent is not None:
            self._results.append(pd.Series(target_percent, index=self.universe, name=self.current_date))

    def initialize(self):
        self.universe = SYMBOLS

    def on_session_end(self):
        raise NotImplementedError("on_session_end should be implemented in subclasses")
        if self.current_date in REBALANCE_DATES:
            _mu, _sigma, _ = self.context.query_covariance(self.current_date, 50)
            if _mu is not None:
                _target_positions = self.strategy(5, 10)(_mu, _sigma)
            else:
                _target_positions = np.repeat(1/5, 5) 
            self.order_pct_to(_target_positions)
    
    def _on_session_end(self):
        self.on_session_end()
    
    def run_pipeline(self):
        self.initialize()
        while True:
            try:
                self.next()
                self._on_session_end()
            except StopIteration:
                break
        return pd.concat(self._results, axis=1).T

class MinVarPipe(Pipeline):
    def initialize(self):
        self.universe = SYMBOLS

    def on_session_end(self):
        if self.current_date in REBALANCE_DATES:
            _mu, _sigma, _ = self.context.query_covariance(self.current_date, 50)
            if _mu is not None:
                _target_positions = MinVarPortfolio(5)(_mu, _sigma)
            else:
                _target_positions = np.repeat(1/5, 5)
            self.order_pct_to(_target_positions)

class MeanVarPipe(Pipeline):
    def initialize(self):
        self.universe = SYMBOLS

    def on_session_end(self):
        if self.current_date in REBALANCE_DATES:
            _mu, _sigma, _ = self.context.query_covariance(self.current_date, 50)
            if _mu is not None:
                _target_positions = MeanVarPortfolio(5, 0.1, _mu)(_mu, _sigma)
            else:
                _target_positions = np.repeat(1/5, 5)

            self.order_pct_to(_target_positions)

class QUPipe(Pipeline):
    def initialize(self):
        self.universe = SYMBOLS

    def on_session_end(self):
        if self.current_date in REBALANCE_DATES:
            _mu, _sigma, _ = self.context.query_covariance(self.current_date, 50)
            if _mu is not None:
                _target_positions = QuadUtilityPortfolio(5, 20)(_mu, _sigma)
            else:
                _target_positions = np.repeat(1/5, 5)

            self.order_pct_to(_target_positions)