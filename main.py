"""Roda o pipeline completo e salva tabelas e gráficos em reports/."""

import pandas as pd

import config
from quant_b3 import plots
from quant_b3.data import CDI_COLUMN, build_dataset
from quant_b3.metrics import summary_table

SUMMARY_LABELS = {
    "cumulative_return": "Retorno acumulado",
    "annualized_return": "Retorno a.a.",
    "annualized_volatility": "Volatilidade a.a.",
    "max_drawdown": "Drawdown máx.",
    "sharpe": "Sharpe",
}


def format_summary(summary: pd.DataFrame) -> pd.DataFrame:
    """Tabela legível: percentuais com 1 casa, Sharpe com 2."""
    formatted = summary.copy()
    for column in ["cumulative_return", "annualized_return", "annualized_volatility", "max_drawdown"]:
        formatted[column] = summary[column].map("{:.1%}".format)
    formatted["sharpe"] = summary["sharpe"].map(lambda value: "-" if pd.isna(value) else f"{value:.2f}")
    formatted.index = [plots.display_name(name) for name in summary.index]
    return formatted.rename(columns=SUMMARY_LABELS)


def run_asset_analysis(prices: pd.DataFrame) -> pd.DataFrame:
    """Fase 2: métricas por ativo, tabela-resumo e gráficos."""
    summary = summary_table(prices, CDI_COLUMN, config.TRADING_DAYS_PER_YEAR)
    summary.to_csv(config.REPORTS_DIR / "summary.csv")

    plots.plot_normalized_prices(
        prices, config.TICKERS, config.BENCHMARK, CDI_COLUMN, config.FIGURES_DIR / "normalized_prices.png"
    )
    plots.plot_drawdowns(prices, config.TICKERS, config.BENCHMARK, config.FIGURES_DIR / "drawdowns.png")
    plots.plot_risk_return(summary, CDI_COLUMN, config.FIGURES_DIR / "risk_return.png")
    return summary


def main() -> None:
    """Ponto de entrada do pipeline."""
    prices = build_dataset(
        [*config.TICKERS, config.BENCHMARK],
        config.START_DATE,
        config.END_DATE,
        config.DATA_DIR,
        config.CDI_SGS_SERIES,
    )
    print(f"Dados: {len(prices)} pregões de {prices.index[0]:%d/%m/%Y} a {prices.index[-1]:%d/%m/%Y}\n")

    summary = run_asset_analysis(prices)
    print(format_summary(summary).to_string())
    print(f"\nRelatório salvo em {config.REPORTS_DIR}")


if __name__ == "__main__":
    main()
