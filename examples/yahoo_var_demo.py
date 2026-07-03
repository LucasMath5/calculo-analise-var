"""Calcula VaR para preços reais obtidos pelo Yahoo Finance."""

import argparse
from pathlib import Path
import sys

# Permite executar este arquivo diretamente a partir da raiz do projeto.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.backtesting import (
    calculate_var_violations,
    christoffersen_conditional_coverage_test,
    christoffersen_independence_test,
    kupiec_test,
)
from src.market_data import download_yahoo_prices
from src.returns import calculate_simple_returns
from src.var_methods import historical_var, normal_parametric_var


def parse_arguments() -> argparse.Namespace:
    """Lê as opções da demonstração pela linha de comando."""
    parser = argparse.ArgumentParser(
        description="Calcula e avalia o VaR de um ativo do Yahoo Finance."
    )
    parser.add_argument(
        "ticker",
        nargs="?",
        default="PETR4.SA",
        help="ticker do Yahoo Finance (padrão: PETR4.SA)",
    )
    parser.add_argument(
        "--period",
        default="2y",
        help="período histórico, por exemplo 6mo, 1y, 2y ou 5y (padrão: 2y)",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        help="nível de confiança do VaR (padrão: 0.95)",
    )
    return parser.parse_args()


def main() -> None:
    """Baixa preços reais e apresenta métricas de VaR e backtesting."""
    arguments = parse_arguments()
    prices = download_yahoo_prices(arguments.ticker, arguments.period)
    returns = calculate_simple_returns(prices)

    historical = historical_var(returns, arguments.confidence)
    parametric = normal_parametric_var(returns, arguments.confidence)
    violations = calculate_var_violations(returns, historical)
    kupiec_result = kupiec_test(violations, arguments.confidence)
    independence_result = christoffersen_independence_test(violations)
    conditional_result = christoffersen_conditional_coverage_test(
        violations,
        arguments.confidence,
    )

    start_date = prices.index.min().date()
    end_date = prices.index.max().date()

    print("Cálculo e Análise de Value at Risk — Yahoo Finance")
    print(f"Ativo: {arguments.ticker.upper()}")
    print(f"Período disponível: {start_date} a {end_date}")
    print(f"Observações de preço: {len(prices)}")
    print(f"Nível de confiança: {arguments.confidence:.0%}")
    print(f"VaR histórico: {historical:.4%}")
    print(f"VaR paramétrico normal: {parametric:.4%}")
    print(f"Violações do VaR histórico: {int(violations.sum())}")
    print(f"Teste de Kupiec (p-valor): {kupiec_result['p_value']:.4f}")
    print(
        "Independência de Christoffersen (p-valor): "
        f"{independence_result['p_value']:.4f}"
    )
    print(
        "Cobertura condicional de Christoffersen (p-valor): "
        f"{conditional_result['p_value']:.4f}"
    )
    print("Aviso: análise educacional; não constitui recomendação financeira.")


if __name__ == "__main__":
    main()
