"""Parâmetros do projeto: ativos, período de análise e caminhos."""

from datetime import date
from pathlib import Path

TICKERS: list[str] = ["ITUB4.SA", "BBDC4.SA", "PETR4.SA", "VALE3.SA", "WEGE3.SA"]
BENCHMARK: str = "^BVSP"
CDI_SGS_SERIES: int = 12

START_DATE: date = date(2021, 1, 1)
END_DATE: date = date(2026, 1, 1)

TRADING_DAYS_PER_YEAR: int = 252

ROOT_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = ROOT_DIR / "data"
FIGURES_DIR: Path = ROOT_DIR / "reports" / "figures"
