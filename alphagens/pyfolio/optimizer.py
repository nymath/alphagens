from abc import ABC, abstractmethod
import numpy as np
from scipy.optimize import minimize


class BaseOptimizer(ABC):
 
    def __init__(self, mu, cov):
        self.mu = mu
        self.cov = cov
        self.solution = None
        self.n_assets = len(self.mu)
    
    @abstractmethod
    def objective_function(self, weights):
        raise NotImplementedError("should implement in the derived class")

    @abstractmethod
    def constraints(self):
        raise NotImplementedError("should implement in the derived class")
    
    @abstractmethod
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))

    def _optimize(self):
        self.solution = minimize(
            lambda weights: self.objective_function(weights), 
            self.initial_guess(), 
            method='SLSQP', 
            bounds=self.bounds(), 
            constraints=self.constraints()
            )

    def get_optimal_weights(self):
        return self.solution.x

    def initial_guess(self):
        init = np.random.uniform(0, 1, size=self.n_assets)
        return init / np.sum(init)
    
    def run(self):
        self._optimize()
        if self.solution.x is None:
            return "FAILED"
        else:
            return "SUCCESS"

    def __call__(self):
        self._optimize()
        if self.solution.x is None:
            return "FAILED"
        else:
            return "SUCCESS"
    

class MinVarPortfolio(BaseOptimizer):

    def __init__(self, mu, cov):
        super().__init__(mu, cov)
    
    def objective_function(self, weights):
        mu = self.mu
        cov = self.cov
        portfolio_mean = weights.T @ mu
        portfolio_variance = weights.T @ cov @ weights
        max_obj = - portfolio_variance
        return - max_obj

    def constraints(self):
        return ({'type': 'eq', 
                 'fun': lambda weights: np.sum(weights) - 1})
    
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))
    

class MeanVarPortfolio(BaseOptimizer):

    def __init__(self, mu, cov, target_return):
        super().__init__(mu, cov)
        self.target_return = target_return

    def objective_function(self, weights):
        portfolio_mean = weights.T @ self.mu
        portfolio_variance = weights.T @ self.cov @ weights
        max_obj = - portfolio_variance
        return - max_obj

    def constraints(self):
        return ({'type': 'eq', 
                 'fun': lambda weights: np.sum(weights) - 1},
                {'type': 'eq',
                 'fun': lambda weights: weights.T @ self.mu - self.target_return})
    
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))
    

class QuadraticUtilityPortfolio(BaseOptimizer):
    def __init__(self, mu, cov, penalty):
        super().__init__(mu, cov)
        self.penalty = penalty

    def objective_function(self, weights):
        portfolio_mean = weights.T @ self.mu
        portfolio_variance = weights.T @ self.cov @ weights
        max_obj =  portfolio_mean - 0.5 * self.penalty * portfolio_variance
        return - max_obj

    def constraints(self):
        return ({'type': 'eq', 
                 'fun': lambda weights: np.sum(weights) - 1})
    
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))