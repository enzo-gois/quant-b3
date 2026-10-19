from datetime import date

import numpy as np
import pandas as pd
import pytest

from quant_b3.data import clean_prices, cdi_index, split_date_range


def test_split_date_range_covers_period_without_gaps_or_overlap():
    windows = split_date_range(date(2020, 1, 1), date(2020, 1, 10), max_days=4)

    assert windows == [
        (date(2020, 1, 1), date(2020, 1, 4)),
        (date(2020, 1, 5), date(2020, 1, 8)),
        (date(2020, 1, 9), date(2020, 1, 10)),
    ]


def test_clean_prices_drops_holidays_and_fills_short_gaps():
    days = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"])
    prices = pd.DataFrame(
        {"A": [np.nan, 10.0, np.nan, 12.0], "B": [np.nan, 20.0, 21.0, 22.0]}, index=days
    )

    cleaned = clean_prices(prices)

    assert cleaned.index.tolist() == days[1:].tolist()
    assert cleaned["A"].tolist() == [10.0, 10.0, 12.0]


def test_clean_prices_does_not_fill_long_gaps():
    days = pd.bdate_range("2024-01-01", periods=5)
    prices = pd.DataFrame(
        {"A": [10.0, np.nan, np.nan, np.nan, 11.0], "B": [1.0, 2.0, 3.0, 4.0, 5.0]}, index=days
    )

    cleaned = clean_prices(prices, max_gap_days=1)

    assert cleaned.index.tolist() == [days[0], days[1], days[4]]


def test_cdi_index_applies_rate_from_previous_day():
    rate_days = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    rates = pd.Series([0.01, 0.02, 0.03], index=rate_days)

    index = cdi_index(rates, rate_days)

    assert index.tolist() == pytest.approx([1.0, 1.01, 1.01 * 1.02])


def test_cdi_index_accrues_days_without_trading():
    rate_days = pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04"])
    rates = pd.Series([0.01, 0.02, 0.03], index=rate_days)
    trading_days = pd.to_datetime(["2024-01-02", "2024-01-04"])

    index = cdi_index(rates, trading_days)

    assert index.tolist() == pytest.approx([1.0, 1.01 * 1.02])
