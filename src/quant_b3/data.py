"""Coleta de preços (yfinance) e do CDI (SGS/Banco Central), com cache em CSV."""

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

CDI_COLUMN = "CDI"
SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series}/dados"
SGS_MAX_DAYS_PER_REQUEST = 3650
SGS_DATE_FORMAT = "%d/%m/%Y"
MAX_FORWARD_FILL_DAYS = 5


def download_prices(tickers: list[str], start: date, end: date) -> pd.DataFrame:
    """Fechamentos diários ajustados por dividendos e desdobramentos (end exclusivo)."""
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"].reindex(columns=tickers)
    missing = prices.columns[prices.isna().all()].tolist()
    if missing:
        raise RuntimeError(f"Sem dados no Yahoo Finance para: {missing}")
    prices.columns.name = None
    prices.index.name = "date"
    return prices


def split_date_range(start: date, end: date, max_days: int) -> list[tuple[date, date]]:
    """Divide [start, end] (inclusivo) em janelas consecutivas de até max_days dias."""
    windows = []
    window_start = start
    while window_start <= end:
        window_end = min(window_start + timedelta(days=max_days - 1), end)
        windows.append((window_start, window_end))
        window_start = window_end + timedelta(days=1)
    return windows


def download_cdi(start: date, end: date, series: int = 12) -> pd.Series:
    """Taxa CDI diária em decimal (0.0005 = 0,05% ao dia), com end exclusivo."""
    last_day = end - timedelta(days=1)
    frames = []
    for window_start, window_end in split_date_range(start, last_day, SGS_MAX_DAYS_PER_REQUEST):
        response = requests.get(
            SGS_URL.format(series=series),
            params={
                "formato": "json",
                "dataInicial": window_start.strftime(SGS_DATE_FORMAT),
                "dataFinal": window_end.strftime(SGS_DATE_FORMAT),
            },
            timeout=30,
        )
        response.raise_for_status()
        frames.append(pd.DataFrame(response.json()))

    records = pd.concat(frames, ignore_index=True)
    rates = pd.Series(
        records["valor"].astype(float).to_numpy() / 100,
        index=pd.DatetimeIndex(pd.to_datetime(records["data"], format=SGS_DATE_FORMAT), name="date"),
        name=CDI_COLUMN,
    )
    return rates[~rates.index.duplicated()].sort_index()


def clean_prices(prices: pd.DataFrame, max_gap_days: int = MAX_FORWARD_FILL_DAYS) -> pd.DataFrame:
    """Mantém só dias com pregão e repete o último preço em lacunas curtas."""
    trading_days = prices.dropna(how="all")
    return trading_days.ffill(limit=max_gap_days).dropna()


def cdi_index(daily_rates: pd.Series, trading_days: pd.DatetimeIndex) -> pd.Series:
    """Valor acumulado de R$ 1 aplicado no CDI, observado em cada dia de pregão.

    A taxa publicada no dia D remunera de D para D+1, por isso o shift(1).
    """
    accumulated = (1 + daily_rates).cumprod().shift(1, fill_value=1.0)
    all_days = accumulated.index.union(trading_days)
    return accumulated.reindex(all_days).ffill().reindex(trading_days).rename(CDI_COLUMN)


def _read_cache(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, index_col="date", parse_dates=["date"])


def _write_cache(data: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path)


def load_prices(tickers: list[str], start: date, end: date, cache_dir: Path) -> pd.DataFrame:
    """Preços brutos do cache; baixa de novo se o arquivo não existir ou faltar ticker."""
    path = cache_dir / f"prices_{start}_{end}.csv"
    if path.exists():
        cached = _read_cache(path)
        if set(tickers) <= set(cached.columns):
            return cached[tickers]
    prices = download_prices(tickers, start, end)
    _write_cache(prices, path)
    return prices


def load_cdi(start: date, end: date, cache_dir: Path, series: int = 12) -> pd.Series:
    """Taxas diárias do CDI do cache, ou da API do Banco Central."""
    path = cache_dir / f"cdi_{start}_{end}.csv"
    if path.exists():
        return _read_cache(path)[CDI_COLUMN]
    rates = download_cdi(start, end, series)
    _write_cache(rates.to_frame(), path)
    return rates


def build_dataset(
    tickers: list[str], start: date, end: date, cache_dir: Path, cdi_series: int = 12
) -> pd.DataFrame:
    """Tabela final: uma coluna por ativo + coluna CDI (acumulado), em dias de pregão."""
    prices = clean_prices(load_prices(tickers, start, end, cache_dir))
    rates = load_cdi(start, end, cache_dir, cdi_series)
    prices[CDI_COLUMN] = cdi_index(rates, prices.index)
    return prices.dropna()
