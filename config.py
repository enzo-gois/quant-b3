"""Parâmetros do projeto: ativos, período de análise e constantes."""

from datetime import date
from pathlib import Path

# --- Ativos -----------------------------------------------------------------
# Sufixo ".SA" = ação negociada na B3 (é como o Yahoo Finance identifica).
TICKERS: list[str] = ["ITUB4.SA", "BBDC4.SA", "PETR4.SA", "VALE3.SA", "WEGE3.SA"]

# Ibovespa: índice de referência ("benchmark") para comparar os ativos.
BENCHMARK: str = "^BVSP"

# Série 12 do SGS (Banco Central) = taxa CDI diária, em % ao dia.
CDI_SGS_SERIES: int = 12

# --- Período de análise -----------------------------------------------------
# TODO(human): defina START_DATE e END_DATE (janela de ~5 anos).
START_DATE = date(2021, 1, 1)
END_DATE = date(2026, 1, 1)

# --- Constantes -------------------------------------------------------------
# Número aproximado de dias de pregão (dias úteis) em um ano na B3.
TRADING_DAYS_PER_YEAR: int = 252

# --- Caminhos ---------------------------------------------------------------
ROOT_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = ROOT_DIR / "data"
FIGURES_DIR: Path = ROOT_DIR / "reports" / "figures"
