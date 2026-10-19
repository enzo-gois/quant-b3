"""Gráficos do relatório, salvos em PNG."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import PercentFormatter

from quant_b3.metrics import drawdown

# ordem fixa: a cor segue o ativo, nunca a posição no gráfico
SERIES_PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"

DISPLAY_NAMES = {"^BVSP": "Ibovespa"}


def display_name(ticker: str) -> str:
    """'ITUB4.SA' -> 'ITUB4', '^BVSP' -> 'Ibovespa'."""
    return DISPLAY_NAMES.get(ticker, ticker.removesuffix(".SA"))


def asset_colors(assets: list[str]) -> dict[str, str]:
    """Cor categórica fixa para cada ativo, na ordem recebida."""
    return dict(zip(assets, SERIES_PALETTE))


def _new_figure(nrows: int = 1, ncols: int = 1, **kwargs) -> tuple[Figure, Axes]:
    fig, axes = plt.subplots(nrows, ncols, facecolor=SURFACE, **kwargs)
    for ax in fig.axes:
        ax.set_facecolor(SURFACE)
        ax.grid(color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(colors=TEXT_SECONDARY, labelsize=9, length=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
    return fig, axes


def _save(fig: Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return path


def _title(ax: Axes, title: str, subtitle: str = "") -> None:
    ax.set_title(title, loc="left", fontsize=13, color=TEXT_PRIMARY, pad=22 if subtitle else 10)
    if subtitle:
        ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9, color=TEXT_SECONDARY)


def plot_normalized_prices(
    prices: pd.DataFrame, assets: list[str], benchmark: str, risk_free: str, path: Path
) -> Path:
    """Evolução de R$ 100 investidos em cada ativo, no Ibovespa e no CDI."""
    normalized = prices / prices.iloc[0] * 100
    colors = asset_colors(assets)
    fig, ax = _new_figure(figsize=(10, 5.5))

    for asset in assets:
        ax.plot(normalized[asset], color=colors[asset], linewidth=1.6, label=display_name(asset))
    ax.plot(normalized[benchmark], color=TEXT_PRIMARY, linewidth=2.2, label=display_name(benchmark))
    ax.plot(normalized[risk_free], color=TEXT_SECONDARY, linewidth=2, linestyle="--", label=risk_free)

    ax.axhline(100, color=TEXT_SECONDARY, linewidth=0.8)
    _title(ax, "R$ 100 investidos no início do período", "Preços ajustados por proventos; CDI acumulado")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1), labelcolor=TEXT_PRIMARY)
    return _save(fig, path)


def plot_drawdowns(prices: pd.DataFrame, assets: list[str], benchmark: str, path: Path) -> Path:
    """Um painel por ativo com a queda em relação ao topo anterior."""
    colors = asset_colors(assets) | {benchmark: TEXT_PRIMARY}
    panels = [*assets, benchmark]
    drawdowns = drawdown(prices[panels])
    ncols = 3
    nrows = -(-len(panels) // ncols)
    fig, axes = _new_figure(nrows, ncols, figsize=(12, 3.2 * nrows), sharex=True, sharey=True)

    for ax, asset in zip(fig.axes, panels):
        series = drawdowns[asset]
        ax.fill_between(series.index, series, 0, color=colors[asset], alpha=0.25, linewidth=0)
        ax.plot(series, color=colors[asset], linewidth=1.2)
        worst_day = series.idxmin()
        ax.annotate(
            f"{series.min():.0%}",
            (worst_day, series.min()),
            xytext=(6, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            color=TEXT_PRIMARY,
        )
        ax.set_title(display_name(asset), loc="left", fontsize=11, color=TEXT_PRIMARY)
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    for ax in fig.axes[len(panels):]:
        ax.set_visible(False)
    fig.axes[0].set_ylim(drawdowns.min().min() * 1.1, 0.02)

    fig.suptitle("Drawdown: queda desde o último topo", x=0.01, ha="left", fontsize=13, color=TEXT_PRIMARY)
    fig.tight_layout()
    return _save(fig, path)


def plot_risk_return(summary: pd.DataFrame, risk_free: str, path: Path) -> Path:
    """Volatilidade x retorno anualizado, com o CDI como referência."""
    fig, ax = _new_figure(figsize=(8, 5.5))
    risky = summary.drop(index=risk_free)

    ax.scatter(
        risky["annualized_volatility"], risky["annualized_return"],
        s=70, color=SERIES_PALETTE[0], edgecolor=SURFACE, linewidth=2, zorder=3,
    )
    for asset, row in risky.iterrows():
        ax.annotate(
            display_name(asset),
            (row["annualized_volatility"], row["annualized_return"]),
            xytext=(7, 4),
            textcoords="offset points",
            fontsize=9,
            color=TEXT_PRIMARY,
        )

    cdi_return = summary.loc[risk_free, "annualized_return"]
    ax.axhline(cdi_return, color=TEXT_SECONDARY, linewidth=1.2, linestyle="--")
    ax.text(ax.get_xlim()[0], cdi_return, f" CDI {cdi_return:.1%} a.a.", va="bottom", fontsize=9, color=TEXT_SECONDARY)

    ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.set_xlabel("Volatilidade anualizada", color=TEXT_SECONDARY, fontsize=9)
    ax.set_ylabel("Retorno anualizado", color=TEXT_SECONDARY, fontsize=9)
    _title(ax, "Risco x retorno", "Acima da linha tracejada = rendeu mais que o CDI")
    return _save(fig, path)
