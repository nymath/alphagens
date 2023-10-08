from abc import ABC, abstractmethod
import numpy as np
from scipy.optimize import minimize


class AbstractPortfolioOptimization(ABC):
    
    def __init__(self, n_assets):
        self.solution = None
        self.n_assets = n_assets
    
    @abstractmethod
    def objective_function(self, weights, mu, cov):
        raise NotImplementedError("should implement in the derived class")

    @abstractmethod
    def constraints(self):
        raise NotImplementedError("should implement in the derived class")
    
    @abstractmethod
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))

    def _optimize(self, mu, cov):
        self.solution = minimize(
            lambda weights: self.objective_function(weights, mu, cov), 
            self.initial_guess(), 
            method='SLSQP', 
            bounds=self.bounds(), 
            constraints=self.constraints()
            )

    def get_optimal_weights(self):
        if self.solution is not None:
            return self.solution.x
        else:
            return "No solution found yet. Please run the optimize method first."

    def initial_guess(self):
        init = np.random.uniform(0, 1, size=self.n_assets)
        return init / np.sum(init)

    def __call__(self, mu, cov):
        self._optimize(mu, cov)
        return self.solution.x


class MinVarPortfolio(AbstractPortfolioOptimization):

    def __init__(self, n_assets):
        super().__init__(n_assets)
    
    def objective_function(self, weights, mu, cov):
        portfolio_mean = weights.T @ mu
        portfolio_variance = weights.T @ cov @ weights
        max_obj = - portfolio_variance
        return - max_obj

    def constraints(self):
        return ({'type': 'eq', 
                 'fun': lambda weights: np.sum(weights) - 1})
    
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))
    

class MeanVarPortfolio(AbstractPortfolioOptimization):

    def __init__(self, n_assets, target_return, mean_return):
        super().__init__(n_assets)
        self.target_return = target_return
        self.mean_return = mean_return

    def objective_function(self, weights, mu, cov):
        portfolio_mean = weights.T @ mu
        portfolio_variance = weights.T @ cov @ weights
        max_obj = - portfolio_variance
        return - max_obj

    def constraints(self):
        return ({'type': 'eq', 
                 'fun': lambda weights: np.sum(weights) - 1},
                {'type': 'eq',
                 'fun': lambda weights: weights.T @ self.mean_return - self.target_return})
    
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))
    

class QuadUtilityPortfolio(AbstractPortfolioOptimization):
    def __init__(self, n_assets, penalty):
        super().__init__(n_assets)
        self.penalty_coefficient = penalty

    def objective_function(self, weights, mu, cov):
        portfolio_mean = weights.T @ mu
        portfolio_variance = weights.T @ cov @ weights
        max_obj =  portfolio_mean - 0.5 * self.penalty_coefficient * portfolio_variance
        return - max_obj

    def constraints(self):
        return ({'type': 'eq', 
                 'fun': lambda weights: np.sum(weights) - 1})
    
    def bounds(self):
        return tuple((0, 1) for _ in range(self.n_assets))


class AnalyticMinVarPortfolio(AbstractPortfolioOptimization):

    def __init__(self, n_assets):
        super().__init__(n_assets)

    def objective_function(self, weights, mu, cov):
        pass

    def constraints(self):
        pass

    def bounds(self):
        pass

    def __call__(self, mu, cov):
        iota = np.repeat(1, self.n_assets)
        try:
            inv_cov = np.linalg.inv(cov)
            target_position = (inv_cov @ iota) / (iota.T @ inv_cov @ iota)

        except np.linalg.LinAlgError:
            print("uninvertiable covariance matrix detected! returns the naive weights")
            target_position = np.repeat(1/self.n_assets, self.n_assets)

        return target_position


class AnalyticMeanVarPortfolio(AbstractPortfolioOptimization):

    def __init__(self, n_assets, target_return):
        super().__init__(n_assets)
        self.target_return = target_return

    def objective_function(self, weights, mu, cov):
        pass

    def constraints(self):
        pass

    def bounds(self):
        pass

    def __call__(self, mu, cov):
        iota = np.repeat(1, self.n_assets)
        try:
            inv_cov = np.linalg.inv(cov)
            A = mu.T @ inv_cov @ mu
            B = iota.T @ inv_cov @ mu
            C = mu.T @ inv_cov @ iota
            D = iota.T @ inv_cov @ iota

            y = D / (A*D - B*C) * inv_cov @ mu - C / (A*D - B*C) * inv_cov @ iota
            z = A / (A*D - B*C) * inv_cov @ iota - B / (A*D - B*C) * inv_cov @ mu
            target_position = self.target_return * y + z
        except np.linalg.LinAlgError:
            print("uninvertiable covariance matrix detected!")
            target_position = np.repeat(1/len(self.n_assets), self.n_assets)

        return target_position
    

class AnalyticQuadUtilityPortfolio(AbstractPortfolioOptimization):
    def __init__(self, n_assets, penalty):
        super().__init__(n_assets)
        self.penalty = penalty

    def objective_function(self, weights, mu, cov):
        pass

    def constraints(self):
        pass

    def bounds(self):
        pass

    def __call__(self, mu, cov):
        alpha = self.penalty
        iota = np.repeat(1, self.n_assets)

        try:
            inv_cov = np.linalg.inv(cov)
            gamma = ( iota.T @ inv_cov @ mu) / (iota.T @ inv_cov @ iota)
            target_position = ( inv_cov @ iota) / (iota.T @ inv_cov @ iota) + (1/alpha) * inv_cov @ (mu - gamma * iota)

        except np.linalg.LinAlgError:
            print("uninvertiable covariance matrix detected!")
            target_position = np.repeat(1/len(self.n_assets), self.n_assets)
        
        return target_position