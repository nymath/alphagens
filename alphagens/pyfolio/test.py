from abc import ABC, abstractmethod
import numpy as np
from scipy.optimize import minimize


class AbstractPortfolioOptimization(ABC):
    def __init__(self, mu, Sigma):
        self.mu = mu
        self.Sigma = Sigma
        self.num_assets = len(mu)
        self.solution = None
    
    @abstractmethod
    def objective_function(self, weights):
        raise NotImplementedError("should implement in the derived class")

    @abstractmethod
    def constraints(self):
        raise NotImplementedError("should implement in the derived class")

    def optimize(self):
        self.solution = minimize(self.objective_function, self.initial_guess(), method='SLSQP', bounds=self.bounds(), constraints=self.constraints())

    def get_optimal_weights(self):
        if self.solution is not None:
            return self.solution.x
        else:
            return "No solution found yet. Please run the optimize method first."

    def initial_guess(self):
        init = np.random.uniform(0, 1, size=self.num_assets)
        return init / np.sum(init)

    def bounds(self):
        return tuple((0, 1) for _ in range(self.num_assets))


class MinVariancePortfolio(AbstractPortfolioOptimization):

    def objective_function(self, weights):
        portfolio_mean = weights.T @ self.mu
        portfolio_variance = weights.T @ self.Sigma @ weights
        # print(f"Portfolio Variance: {portfolio_variance} for weights: {weights}") 
        max_obj = portfolio_mean - portfolio_variance
        return - max_obj

    def constraints(self):
        return ({'type': 'eq', 
                 'fun': lambda weights: np.sum(weights) - 1})

# 创建对象
np.random.seed(42)
data = np.random.normal(0, 0.03, (252, 5))

mu = np.mean(data, axis=0)
Sigma = np.cov(data, rowvar=False)

np.random.seed(49)
portfolio_opt = MinVariancePortfolio(mu, Sigma)
portfolio_opt.optimize()
print([round(x, 4) for x in portfolio_opt.get_optimal_weights()])