"""Gera os gráficos usados na documentação do projeto."""

from pathlib import Path
import sys

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# Permite executar este arquivo diretamente a partir da raiz do projeto.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.returns import calculate_simple_returns
from src.var_methods import historical_var, normal_parametric_var


def generate_synthetic_data() -> tuple[pd.Series, pd.Series]:
    """Reproduz os preços e retornos sintéticos do exemplo principal."""
    random_generator = np.random.default_rng(seed=42)
    simulated_returns = random_generator.normal(loc=0.0004, scale=0.012, size=500)
    prices = pd.Series(
        100 * np.cumprod(1 + simulated_returns),
        name="synthetic_price",
    )
    return prices, calculate_simple_returns(prices)


def save_price_chart(prices: pd.Series, output_path: Path) -> None:
    """Salva o gráfico da trajetória dos preços sintéticos."""
    figure, axis = plt.subplots(figsize=(11, 4.8))
    axis.plot(prices.index, prices, color="#2563eb", linewidth=1.8)
    axis.fill_between(prices.index, prices, prices.min(), color="#93c5fd", alpha=0.2)
    axis.set_title("Trajetória da série sintética de preços", loc="left", weight="bold")
    axis.set_xlabel("Observação")
    axis.set_ylabel("Preço")
    axis.grid(alpha=0.2)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def save_var_analysis_chart(
    returns: pd.Series,
    historical: float,
    parametric: float,
    output_path: Path,
) -> None:
    """Salva gráficos dos retornos, limites de VaR e sua distribuição."""
    figure, (returns_axis, distribution_axis) = plt.subplots(
        2,
        1,
        figsize=(11, 8),
        gridspec_kw={"height_ratios": [1.3, 1]},
    )

    violations = returns < -historical
    returns_axis.plot(
        returns.index,
        returns,
        color="#64748b",
        linewidth=0.8,
        alpha=0.8,
        label="Retorno diário",
    )
    returns_axis.scatter(
        returns.index[violations],
        returns[violations],
        color="#dc2626",
        s=20,
        zorder=3,
        label="Violação do VaR histórico",
    )
    returns_axis.axhline(
        -historical,
        color="#dc2626",
        linestyle="--",
        linewidth=1.5,
        label=f"VaR histórico ({historical:.2%})",
    )
    returns_axis.axhline(
        -parametric,
        color="#7c3aed",
        linestyle=":",
        linewidth=2,
        label=f"VaR paramétrico ({parametric:.2%})",
    )
    returns_axis.set_title("Retornos e violações de VaR", loc="left", weight="bold")
    returns_axis.set_xlabel("Observação")
    returns_axis.set_ylabel("Retorno")
    returns_axis.yaxis.set_major_formatter(PercentFormatter(1.0))
    returns_axis.grid(alpha=0.2)
    returns_axis.legend(loc="lower right", fontsize=9)

    distribution_axis.hist(
        returns,
        bins=35,
        color="#60a5fa",
        edgecolor="white",
        alpha=0.85,
    )
    distribution_axis.axvline(
        -historical,
        color="#dc2626",
        linestyle="--",
        linewidth=1.8,
        label="Limite histórico",
    )
    distribution_axis.axvline(
        -parametric,
        color="#7c3aed",
        linestyle=":",
        linewidth=2,
        label="Limite paramétrico",
    )
    distribution_axis.set_title("Distribuição dos retornos", loc="left", weight="bold")
    distribution_axis.set_xlabel("Retorno")
    distribution_axis.set_ylabel("Frequência")
    distribution_axis.xaxis.set_major_formatter(PercentFormatter(1.0))
    distribution_axis.grid(axis="y", alpha=0.2)
    distribution_axis.legend(fontsize=9)

    figure.tight_layout(h_pad=2.5)
    figure.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    """Calcula as métricas e atualiza as imagens da documentação."""
    output_directory = PROJECT_ROOT / "docs" / "images"
    output_directory.mkdir(parents=True, exist_ok=True)

    prices, returns = generate_synthetic_data()
    historical = historical_var(returns, confidence_level=0.95)
    parametric = normal_parametric_var(returns, confidence_level=0.95)

    save_price_chart(prices, output_directory / "synthetic_prices.png")
    save_var_analysis_chart(
        returns,
        historical,
        parametric,
        output_directory / "var_analysis.png",
    )

    print(f"Gráficos atualizados em: {output_directory}")


if __name__ == "__main__":
    main()
