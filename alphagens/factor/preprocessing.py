import pandas as pd
import numpy as np
import typing

def get_clean_factor_and_forward_returns(
    factor,
    prices,
    groupby=None,
    binning_by_group=False,
    quantiles=5,
    bins=None,
    periods=(1, 5, 20),
    periods_by_factor = False,
    filter_zscore=20,
    groupby_labels=None,
    zero_aware=False,
    cumulative_returns=True
):
    if periods_by_factor:
        periods = None
    forward_returns = compute_forward_returns(
        factor,
        prices,
        periods,
        periods_by_factor,
        filter_zscore,
        cumulative_returns,
    )

    factor_data = get_clean_factor(
        factor, 
        forward_returns, 
        groupby=groupby,
        groupby_labels=groupby_labels,
        quantiles=quantiles, 
        bins=bins,
        binning_by_group=binning_by_group,
        zero_aware=zero_aware)
    factor_data["factor_quantile"] = factor_data["factor_quantile"].astype(int)
    return factor_data

def get_clean_factor_and_current_returns(
    factor: pd.DataFrame,
    prices: pd.DataFrame,
    groupby: typing.Optional[typing.Union[pd.Series, dict]]=None,
    binning_by_group: bool=False,
    quantiles: typing.Union[int, typing.Iterable[float]]=5,
    bins=None,
    filter_zscore=20,
    groupby_labels=None,
    zero_aware=False,
):

    forward_returns = compute_current_returns(
        factor,
        prices,
    )

    factor_data = get_clean_factor(
        factor, 
        forward_returns, 
        groupby=groupby,
        groupby_labels=groupby_labels,
        quantiles=quantiles, 
        bins=bins,
        binning_by_group=binning_by_group,
        zero_aware=zero_aware)
    return factor_data


def compute_forward_returns_custom(
    factor: pd.DataFrame,
    prices,
    filter_zscore = None,
    cumlative_returns = False,
):
    factor_dateindex = factor.index.levels[0]
    factor_dateindex = factor_dateindex.intersection(prices.index)

    if len(factor_dateindex) == 0:
        raise ValueError("Factor and prices indices don't match")
    raise NotImplementedError("this function has not been implemented yet")


def compute_forward_returns(
    factor: pd.DataFrame,
    prices: pd.DataFrame,
    periods: tuple = (1, ),
    periods_by_factor: bool = False,
    filter_zscore: float = None,
    cumulative_returns: bool = False
) -> pd.DataFrame:
    """create the N period forward returns based on the trading prices

    Parameters
    ----------
    factor : pd.DataFrame
        DataFrame with multiIndex
    prices : pd.DataFrame

    periods : tuple, optional
        _description_, by default (1, )
    filter_zscore : float, optional
        _description_, by default None
    cumulative_returns : bool, optional
        _description_, by default False

    Returns
    -------
    pd.DataFrame
    """
    factor_dateindex = factor.index.get_level_values(0).unique()
    factor_dateindex = factor_dateindex.intersection(prices.index)

    if len(factor_dateindex) == 0:
        raise ValueError("Factor and prices indices don't match: make sure "
                         "they have the same convention in terms of datetimes "
                         "and symbol-names")

    raw_values_dict = {}
    column_list = []

    if not periods_by_factor:
        for period in sorted(periods):
            if cumulative_returns:
                returns = prices.pct_change(period)
            else:
                returns = prices.pct_change()

            forward_returns = returns.shift(-period).reindex(factor_dateindex)

            if filter_zscore is not None:
                mask = abs(forward_returns - forward_returns.mean()) > (filter_zscore * forward_returns.std())
                forward_returns[mask] = np.nan

            label = f"{period}D"

            column_list.append(label)

            raw_values_dict[label] = np.concatenate(forward_returns.values)
    else:
        returns = prices.loc[factor_dateindex].pct_change().fillna(0)
        forward_returns = returns.shift(-1).reindex(factor_dateindex)

        label = "1T"
        column_list.append(label)

        raw_values_dict[label] = np.concatenate(forward_returns.values)

    df = pd.DataFrame.from_dict(raw_values_dict)
    df.set_index(
        pd.MultiIndex.from_product(
            [factor_dateindex, prices.columns],
            names=['date', 'asset']
        ),
        inplace=True
    )
    df = df.reindex(factor.index)

    df = df[column_list]

    df.index.set_names(['date', 'asset'], inplace=True)
    return df

def compute_forward_returns_custom(
    factor: pd.DataFrame,
    prices,
    filter_zscore = None,
    cumlative_returns = False,
):
    factor_dateindex = factor.index.levels[0]
    factor_dateindex = factor_dateindex.intersection(prices.index)

    if len(factor_dateindex) == 0:
        raise ValueError("Factor and prices indices don't match")
    raise NotImplementedError("this function has not been implemented yet")


def compute_current_returns(
    factor: pd.DataFrame,
    prices: pd.DataFrame,
) -> pd.DataFrame:

    factor_dateindex = factor.index.get_level_values(0).unique()
    factor_dateindex = factor_dateindex.intersection(prices.index)

    if len(factor_dateindex) == 0:
        raise ValueError("Factor and prices indices don't match: make sure "
                         "they have the same convention in terms of datetimes "
                         "and symbol-names")

    raw_values_dict = {}
    column_list = []


    returns = prices.pct_change().reindex(factor_dateindex)

    label = "current_returns"

    column_list.append(label)

    raw_values_dict[label] = np.concatenate(returns.values)

    df = pd.DataFrame.from_dict(raw_values_dict)
    df.set_index(
        pd.MultiIndex.from_product(
            [factor_dateindex, prices.columns],
            names=['date', 'asset']
        ),
        inplace=True
    )
    df = df.reindex(factor.index)
    df = df[column_list]
    df.index.set_names(['date', 'asset'], inplace=True)
    return df




def quantize_factor(factor_data,
                    quantiles=5,
                    bins=None,
                    by_group=False,
                    no_raise=False,
                    zero_aware=False):
    """
    Computes period wise factor quantiles.

    Parameters
    ----------
    factor_data : pd.DataFrame - MultiIndex
        A MultiIndex DataFrame indexed by date (level 0) and asset (level 1),
        containing the values for a single alpha factor, forward returns for
        each period, the factor quantile/bin that factor value belongs to, and
        (optionally) the group the asset belongs to.

        - See full explanation in utils.get_clean_factor_and_forward_returns

    quantiles : int or sequence[float]
        Number of equal-sized quantile buckets to use in factor bucketing.
        Alternately sequence of quantiles, allowing non-equal-sized buckets
        e.g. [0, .10, .5, .90, 1.] or [.05, .5, .95]
        Only one of 'quantiles' or 'bins' can be not-None
    bins : int or sequence[float]
        Number of equal-width (valuewise) bins to use in factor bucketing.
        Alternately sequence of bin edges allowing for non-uniform bin width
        e.g. [-4, -2, -0.5, 0, 10]
        Only one of 'quantiles' or 'bins' can be not-None
    by_group : bool, optional
        If True, compute quantile buckets separately for each group.
    no_raise: bool, optional
        If True, no exceptions are thrown and the values for which the
        exception would have been thrown are set to np.NaN
    zero_aware : bool, optional
        If True, compute quantile buckets separately for positive and negative
        signal values. This is useful if your signal is centered and zero is
        the separation between long and short signals, respectively.

    Returns
    -------
    factor_quantile : pd.Series
        Factor quantiles indexed by date and asset.
    """
    if not ((quantiles is not None and bins is None) or
            (quantiles is None and bins is not None)):
        raise ValueError('Either quantiles or bins should be provided')

    if zero_aware and not (isinstance(quantiles, int)
                           or isinstance(bins, int)):
        msg = ("zero_aware should only be True when quantiles or bins is an"
               " integer")
        raise ValueError(msg)

    def quantile_calc(x, _quantiles, _bins, _zero_aware, _no_raise):
        try:
            if _quantiles is not None and _bins is None and not _zero_aware:
                return pd.qcut(x, _quantiles, labels=False) + 1
            elif _quantiles is not None and _bins is None and _zero_aware:
                pos_quantiles = pd.qcut(x[x >= 0], _quantiles // 2,
                                        labels=False) + _quantiles // 2 + 1
                neg_quantiles = pd.qcut(x[x < 0], _quantiles // 2,
                                        labels=False) + 1
                return pd.concat([pos_quantiles, neg_quantiles]).sort_index()
            elif _bins is not None and _quantiles is None and not _zero_aware:
                return pd.cut(x, _bins, labels=False) + 1
            elif _bins is not None and _quantiles is None and _zero_aware:
                pos_bins = pd.cut(x[x >= 0], _bins // 2,
                                  labels=False) + _bins // 2 + 1
                neg_bins = pd.cut(x[x < 0], _bins // 2,
                                  labels=False) + 1
                return pd.concat([pos_bins, neg_bins]).sort_index()
        except Exception as e:
            if _no_raise:
                return pd.Series(np.nan, index=x.index)
            raise e

    grouper = [factor_data.index.get_level_values('date')]
    if by_group:
        grouper.append('group')

    factor_quantile = factor_data.groupby(grouper, group_keys=False)['factor'].apply(quantile_calc, quantiles, bins, zero_aware, no_raise)
    factor_quantile.name = 'factor_quantile'

    return factor_quantile.dropna()


def get_clean_factor(factor,
                     forward_returns,
                     groupby=None,
                     binning_by_group=False,
                     quantiles=5,
                     bins=None,
                     groupby_labels=None,
                     zero_aware=False):
    """
    Formats the factor data, forward return data, and group mappings into a
    DataFrame that contains aligned MultiIndex indices of timestamp and asset.
    The returned data will be formatted to be suitable for Alphalens functions.

    It is safe to skip a call to this function and still make use of Alphalens
    functionalities as long as the factor data conforms to the format returned
    from get_clean_factor_and_forward_returns and documented here

    Parameters
    ----------
    factor : pd.Series - MultiIndex
        A MultiIndex Series indexed by timestamp (level 0) and asset
        (level 1), containing the values for a single alpha factor.
        ::
            -----------------------------------
                date    |    asset   |
            -----------------------------------
                        |   AAPL     |   0.5
                        -----------------------
                        |   BA       |  -1.1
                        -----------------------
            2014-01-01  |   CMG      |   1.7
                        -----------------------
                        |   DAL      |  -0.1
                        -----------------------
                        |   LULU     |   2.7
                        -----------------------

    forward_returns : pd.DataFrame - MultiIndex
        A MultiIndex DataFrame indexed by timestamp (level 0) and asset
        (level 1), containing the forward returns for assets.
        Forward returns column names must follow the format accepted by
        pd.Timedelta (e.g. '1D', '30m', '3h15m', '1D1h', etc).
        'date' index freq property must be set to a trading calendar
        (pandas DateOffset), see infer_trading_calendar for more details.
        This information is currently used only in cumulative returns
        computation
        ::
            ---------------------------------------
                       |       | 1D  | 5D  | 10D
            ---------------------------------------
                date   | asset |     |     |
            ---------------------------------------
                       | AAPL  | 0.09|-0.01|-0.079
                       ----------------------------
                       | BA    | 0.02| 0.06| 0.020
                       ----------------------------
            2014-01-01 | CMG   | 0.03| 0.09| 0.036
                       ----------------------------
                       | DAL   |-0.02|-0.06|-0.029
                       ----------------------------
                       | LULU  |-0.03| 0.05|-0.009
                       ----------------------------

    groupby : pd.Series - MultiIndex or dict
        Either A MultiIndex Series indexed by date and asset,
        containing the period wise group codes for each asset, or
        a dict of asset to group mappings. If a dict is passed,
        it is assumed that group mappings are unchanged for the
        entire time period of the passed factor data.
    binning_by_group : bool
        If True, compute quantile buckets separately for each group.
        This is useful when the factor values range vary considerably
        across gorups so that it is wise to make the binning group relative.
        You should probably enable this if the factor is intended
        to be analyzed for a group neutral portfolio
    quantiles : int or sequence[float]
        Number of equal-sized quantile buckets to use in factor bucketing.
        Alternately sequence of quantiles, allowing non-equal-sized buckets
        e.g. [0, .10, .5, .90, 1.] or [.05, .5, .95]
        Only one of 'quantiles' or 'bins' can be not-None
    bins : int or sequence[float]
        Number of equal-width (valuewise) bins to use in factor bucketing.
        Alternately sequence of bin edges allowing for non-uniform bin width
        e.g. [-4, -2, -0.5, 0, 10]
        Chooses the buckets to be evenly spaced according to the values
        themselves. Useful when the factor contains discrete values.
        Only one of 'quantiles' or 'bins' can be not-None
    groupby_labels : dict
        A dictionary keyed by group code with values corresponding
        to the display name for each group.
    max_loss : float, optional
        Maximum percentage (0.00 to 1.00) of factor data dropping allowed,
        computed comparing the number of items in the input factor index and
        the number of items in the output DataFrame index.
        Factor data can be partially dropped due to being flawed itself
        (e.g. NaNs), not having provided enough price data to compute
        forward returns for all factor values, or because it is not possible
        to perform binning.
        Set max_loss=0 to avoid Exceptions suppression.
    zero_aware : bool, optional
        If True, compute quantile buckets separately for positive and negative
        signal values. This is useful if your signal is centered and zero is
        the separation between long and short signals, respectively.
        'quantiles' is None.

    Returns
    -------
    merged_data : pd.DataFrame - MultiIndex
        A MultiIndex Series indexed by date (level 0) and asset (level 1),
        containing the values for a single alpha factor, forward returns for
        each period, the factor quantile/bin that factor value belongs to, and
        (optionally) the group the asset belongs to.

        - forward returns column names follow the format accepted by
          pd.Timedelta (e.g. '1D', '30m', '3h15m', '1D1h', etc)

        - 'date' index freq property (merged_data.index.levels[0].freq) is the
          same as that of the input forward returns data. This is currently
          used only in cumulative returns computation
        ::
           -------------------------------------------------------------------
                      |       | 1D  | 5D  | 10D  |factor|group|factor_quantile
           -------------------------------------------------------------------
               date   | asset |     |     |      |      |     |
           -------------------------------------------------------------------
                      | AAPL  | 0.09|-0.01|-0.079|  0.5 |  G1 |      3
                      --------------------------------------------------------
                      | BA    | 0.02| 0.06| 0.020| -1.1 |  G2 |      5
                      --------------------------------------------------------
           2014-01-01 | CMG   | 0.03| 0.09| 0.036|  1.7 |  G2 |      1
                      --------------------------------------------------------
                      | DAL   |-0.02|-0.06|-0.029| -0.1 |  G3 |      5
                      --------------------------------------------------------
                      | LULU  |-0.03| 0.05|-0.009|  2.7 |  G1 |      2
                      --------------------------------------------------------
    """

    # initial_amount = float(len(factor.index))

    factor_copy = factor.copy()
    factor_copy.index = factor_copy.index.rename(['date', 'asset'])
    factor_copy = factor_copy[np.isfinite(factor_copy)]

    merged_data = forward_returns.copy()
    merged_data['factor'] = factor_copy

    if groupby is not None:
        if isinstance(groupby, dict):
            diff = set(factor_copy.index.get_level_values(
                'asset')) - set(groupby.keys())
            if len(diff) > 0:
                raise KeyError(
                    "Assets {} not in group mapping".format(
                        list(diff)))

            ss = pd.Series(groupby)
            groupby = pd.Series(index=factor_copy.index,
                                data=ss[factor_copy.index.get_level_values(
                                    'asset')].values)

        if groupby_labels is not None:
            diff = set(groupby.values) - set(groupby_labels.keys())
            if len(diff) > 0:
                raise KeyError(
                    "groups {} not in passed group names".format(
                        list(diff)))

            sn = pd.Series(groupby_labels)
            groupby = pd.Series(index=groupby.index,
                                data=sn[groupby.values].values)

        merged_data['group'] = groupby.astype('category')

    merged_data = merged_data.dropna()

    # fwdret_amount = float(len(merged_data.index))

    # no_raise = False if max_loss == 0 else True

    quantile_data = quantize_factor(
        merged_data,
        quantiles,
        bins,
        binning_by_group,
        True,
        zero_aware
    )

    merged_data['factor_quantile'] = quantile_data

    merged_data = merged_data.dropna()

    # binning_amount = float(len(merged_data.index))

    # tot_loss = (initial_amount - binning_amount) / initial_amount
    # fwdret_loss = (initial_amount - fwdret_amount) / initial_amount
    # bin_loss = tot_loss - fwdret_loss

    # print("Dropped %.1f%% entries from factor data: %.1f%% in forward "
    #       "returns computation and %.1f%% in binning phase "
    #       "(set max_loss=0 to see potentially suppressed Exceptions)." %
    #       (tot_loss * 100, fwdret_loss * 100, bin_loss * 100))

    # if tot_loss > max_loss:
    #     message = ("max_loss (%.1f%%) exceeded %.1f%%, consider increasing it."
    #                % (max_loss * 100, tot_loss * 100))
    #     raise MaxLossExceededError(message)
    # else:
    #     print("max_loss is %.1f%%, not exceeded: OK!" % (max_loss * 100))

    return merged_data