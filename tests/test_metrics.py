import math

import numpy as np
import pandas as pd
import pytest

from quant_b3.metrics import (
    annualized_return,
    annualized_volatility,
    cumulative_return,
    drawdown,
    log_returns,
    max_drawdown,
    sharpe_ratio,
    simple_returns,
    summary_table,
)

# 100 -> 110 -> 99 -> 108.9: +10%, -10%, +10%
PRICES = pd.Series([100.0, 110.0, 99.0, 108.9])


def test_simple_returns():
    assert simple_returns(PRICES).tolist() == pytest.approx([0.10, -0.10, 0.10])


def test_log_returns_sum_to_log_of_total_growth():
    returns = log_returns(PRICES)

    assert returns.tolist() == pytest.approx([math.log(1.1), math.log(0.9), math.log(1.1)])
    assert returns.sum() == pytest.approx(math.log(108.9 / 100))


def test_cumulative_return():
    assert cumulative_return(PRICES) == pytest.approx(0.089)


def test_annualized_return_equals_cumulative_when_period_is_one_year():
    assert annualized_return(PRICES, periods_per_year=3) == pytest.approx(0.089)


def test_annualized_return_compounds_half_year_into_full_year():
    assert annualized_return(PRICES, periods_per_year=6) == pytest.approx(1.089**2 - 1)


def test_annualized_volatility():
    # desvio amostral de [0.1, -0.1, 0.1] = 0.11547; x raiz(4) = 0.23094
    returns = simple_returns(PRICES)

    assert annualized_volatility(returns, periods_per_year=4) == pytest.approx(0.230940, abs=1e-6)


def test_drawdown_and_max_drawdown():
    assert drawdown(PRICES).tolist() == pytest.approx([0.0, 0.0, -0.10, -0.01])
    assert max_drawdown(PRICES) == pytest.approx(-0.10)


def test_drawdown_is_zero_for_series_that_only_rises():
    rising = pd.Series([1.0, 2.0, 3.0])

    assert max_drawdown(rising) == 0.0


def test_sharpe_ratio_with_zero_risk_free():
    returns = simple_returns(PRICES)
    risk_free = pd.Series(0.0, index=returns.index)

    # média 0.0333 / desvio 0.11547 x raiz(4)
    assert sharpe_ratio(returns, risk_free, periods_per_year=4) == pytest.approx(0.577350, abs=1e-6)


def test_sharpe_ratio_subtracts_risk_free():
    returns = simple_returns(PRICES)
    risk_free = pd.Series(0.01, index=returns.index)

    assert sharpe_ratio(returns, risk_free, periods_per_year=4) == pytest.approx(0.404145, abs=1e-6)


def test_summary_table_has_one_row_per_asset_and_nan_sharpe_for_risk_free():
    prices = pd.DataFrame({"ACAO": PRICES, "CDI": [1.0, 1.01, 1.0201, 1.030301]})

    table = summary_table(prices, risk_free_column="CDI", periods_per_year=3)

    assert table.index.tolist() == ["ACAO", "CDI"]
    assert table.loc["ACAO", "cumulative_return"] == pytest.approx(0.089)
    assert table.loc["CDI", "max_drawdown"] == 0.0
    assert np.isnan(table.loc["CDI", "sharpe"])
