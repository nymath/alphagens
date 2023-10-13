# AlphaGens

-----

An agent-environment based backtesting framework.

## Event-Driven backtesting 
-----

```python
class BuyAndHold(BaseStrategy):
    def __init__(self, engine, broker, account):
        super().__init__(engine, broker, account)
    
    def before_trading_end(self):
        if self.current_date == self.trade_dates[0]:
            self.account.order_target_pct_to(pd.Series(1, index=["000001"]))
```


## quick start

----

```python
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
```

```python
while True:
    try:
        print(f"current date is {env.current_date}")
        action = agent.take_action(state, env.current_date)
    
        next_state, reward, truncated, terminated, info = env.step(action)
        state = next_state
        returns.append(reward)

    except IndexError:
        break
```
