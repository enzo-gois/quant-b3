"""Métricas de retorno e risco: retorno, volatilidade, drawdown e Sharpe."""

import numpy as np
import pandas as pd

PriceData = pd.Series | pd.DataFrame


def simple_returns(prices: PriceData) -> PriceData:
    """Retorno diário simples: P_t / P_{t-1} - 1."""
    return prices.pct_change().iloc[1:]


def log_returns(prices: PriceData) -> PriceData:
    """Retorno diário logarítmico: ln(P_t / P_{t-1})."""
    return np.log(prices).diff().iloc[1:]


def cumulative_return(prices: PriceData) -> float | pd.Series:
    """Retorno total do período: P_final / P_inicial - 1."""
    return prices.iloc[-1] / prices.iloc[0] - 1


def annualized_return(prices: PriceData, periods_per_year: int = 252) -> float | pd.Series:
    """Taxa anual composta equivalente ao retorno do período (CAGR)."""
    years = (len(prices) - 1) / periods_per_year
    return (1 + cumulative_return(prices)) ** (1 / years) - 1


def annualized_volatility(returns: PriceData, periods_per_year: int = 252) -> float | pd.Series:
    """Desvio padrão dos retornos diários levado para a escala anual."""
    # risco cresce com a raiz do tempo, não linearmente
    return returns.std(ddof=1) * np.sqrt(periods_per_year)


def drawdown(prices: PriceData) -> PriceData:
    """Queda percentual em relação ao maior preço já visto até cada dia."""
    return prices / prices.cummax() - 1


def max_drawdown(prices: PriceData) -> float | pd.Series:
    """Pior queda do topo ao fundo no período (valor negativo)."""
    return drawdown(prices).min()


def sharpe_ratio(
    returns: PriceData, risk_free_returns: pd.Series, periods_per_year: int = 252
) -> float | pd.Series:
    """Retorno acima da taxa livre de risco por unidade de volatilidade, anualizado."""
    excess_returns = returns.sub(risk_free_returns, axis=0)
    return excess_returns.mean() / excess_returns.std(ddof=1) * np.sqrt(periods_per_year)


def summary_table(
    prices: pd.DataFrame, risk_free_column: str, periods_per_year: int = 252
) -> pd.DataFrame:
    """Uma linha por ativo com as métricas principais do período."""
    returns = simple_returns(prices)
    return pd.DataFrame(
        {
            "cumulative_return": cumulative_return(prices),
            "annualized_return": annualized_return(prices, periods_per_year),
            "annualized_volatility": annualized_volatility(returns, periods_per_year),
            "max_drawdown": max_drawdown(prices),
            "sharpe": sharpe_ratio(returns, returns[risk_free_column], periods_per_year),
        }
    )
