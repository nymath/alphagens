import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import typing
from ..utils.visualization import ColorGenerator

class StrategyMetrics:

    """用staticmethod好一些吗? 目前数据格式不是很统一, 还是一个一个算比较好
    """
    annulized_factor: int = 252

    @staticmethod
    def annulized_mean(strategy_returns, annulized_factor=252):
        return np.mean(strategy_returns) * annulized_factor
    
    @staticmethod
    def annulized_std(strategy_returns, annulized_factor=252):
        return np.std(strategy_returns) * np.sqrt(annulized_factor)

    @staticmethod
    def annulized_sharpe_ratio(strategy_returns, rfr=0, annulized_factor=252):
        return (np.mean(strategy_returns- rfr)) / np.std(strategy_returns) * np.sqrt(annulized_factor)
    
    @staticmethod
    def drawdown(strategy_returns: pd.Series) -> (pd.Series, float, int):
        """
        Returns
        -------
        (max drawdown, longest drawdown duration, drawdown series,)
        """
        net_curve = (1+strategy_returns).cumpord()
        cmax = net_curve.cumax()
        rlt = cmax / net_curve - 1
        longest_drawdown = cmax.value_counts().max() - 1
        if isinstance(strategy_returns, pd.Series):
            rlt = pd.Series(rlt, index=strategy_returns.index)
        elif isinstance(strategy_returns, np.ndarray):
            rlt = np.array(rlt)
        return rlt.max(), longest_drawdown, rlt
    
    @staticmethod
    def evaluate(strategy_returns, benchmark_returns=0, rfr=0, annulized_factor=252):
        raise NotImplementedError
        result = {}
        result["mean"] = StrategyMetrics.annulized_mean(strategy_returns, annulized_factor)
        result["std"] = StrategyMetrics.annulized_std(strategy_returns, annulized_factor)
        result["sharpe_ratio"] = StrategyMetrics.annulized_sharpe_ratio(strategy_returns, rfr, annulized_factor)

    @staticmethod
    def reg_stats(strategy_returns, benchmark_returns, rfr=0, annulize_factor=252):
        y = strategy_returns - rfr
        X = benchmark_returns.reshape(-1, 1) - rfr
        model = LinearRegression()
        model.fit(X, y)
        annulized_alpha = model.intercept_ * annulize_factor
        beta = model.coef_[0]
        residuals = y - model.predict(X)
        annulized_residual_std = np.std(residuals) * np.sqrt(annulize_factor)
        return annulized_alpha, beta, annulized_residual_std

    @staticmethod
    def plot_heatmap_of_monthly_returns(
        strategy_returns: pd.Series, 
        figsize: tuple[float] = (12, 10),
        title: str = 'Monthly Returns Heatmap',
        vlim: tuple[float] = (-0.3, 0.3),
        dpi: int = 100,
    ):
        tmp = strategy_returns.resample("M").sum()
        tmp.name = "monthly returns"
        tmp = pd.DataFrame(tmp)
        tmp['year'] = tmp.index.year
        tmp['month'] = tmp.index.month
        bb = tmp.pivot_table(tmp, index=tmp["year"], columns=tmp["month"])
        bb.columns.name = None
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=figsize, dpi=dpi)
        ax = sns.heatmap(bb.values, annot=True, cmap="RdYlGn_r", fmt=".2%", linewidths=0.5, linecolor='white', 
                         yticklabels=bb.index, xticklabels=bb.columns, vmin=vlim[0], vmax=vlim[1], ax=ax)
        ax.set_title(title)
        ax.set_xlabel('Month')
        ax.set_ylabel('Year')
        fig.tight_layout()
        return fig, ax

    @staticmethod
    def integrated_informations_by_year(
        strategy_returns,
    ):
        pass

    @staticmethod
    def beta():
        raise Warning("to get beta, call reg_stats")
    
    @staticmethod
    def alpha():
        raise Warning("to get alpha, call reg_stats")
    

class FactorMetrics:
    
    @staticmethod
    def ic_series(factor_scores, forward_returns, method="pearson") -> pd.Series:
        """_summary_
        caculate the 
        - `mean-IC`
        - `ICIR`

        Parameters
        ----------
        factor_scores : _type_
            _description_
        forward_returns : _type_
            _description_
        method : str, optional
            _description_, by default "pearson"

        Returns
        -------
        pd.Series
            _description_
        """
        pass

    @staticmethod
    def plot_pnl_by_groups(strategies_pnls: pd.DataFrame, dpi=100):
        colors = ColorGenerator(5).data
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,8), dpi=dpi)
        for idx, name in enumerate(strategies_pnls.columns):
            pnl = strategies_pnls[name]
            ax.plot(pnl, label=f"group_{idx}", color=colors[idx])
        ax.legend()
        ax.set_xlabel("Date")
        ax.set_ylabel("pnl")
        ax.grid()
        fig.tight_layout()
        return fig, ax

    @staticmethod
    def cum_ic_series():
        raise NotImplementedError

    @staticmethod
    def long_short_returns(integrated_factors) -> pd.Series:
        pass

    @staticmethod
    def group_returns(integrated_factors) -> pd.DataFrame:
        pass

    @staticmethod
    def turnover():
        raise NotImplementedError
    
    @staticmethod
    def fitness():
        pass

    staticmethod
    def margin():
        pass
    

