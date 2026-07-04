"""Demonstração dos cálculos de VaR usando preços sintéticos."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd

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
from src.returns import calculate_simple_returns
from src.var_methods import (
    historical_expected_shortfall,
    historical_var,
    normal_parametric_expected_shortfall,
    normal_parametric_var,
)


def main() -> None:
    """Gera dados sintéticos e apresenta métricas básicas de VaR."""
    random_generator = np.random.default_rng(seed=42)
    simulated_returns = random_generator.normal(loc=0.0004, scale=0.012, size=500)
    prices = pd.Series(
        100 * np.cumprod(1 + simulated_returns),
        name="synthetic_price",
    )

    returns = calculate_simple_returns(prices)
    confidence_level = 0.95
    historical = historical_var(returns, confidence_level)
    parametric = normal_parametric_var(returns, confidence_level)
    historical_es = historical_expected_shortfall(returns, confidence_level)
    parametric_es = normal_parametric_expected_shortfall(
        returns,
        confidence_level,
    )
    violations = calculate_var_violations(returns, historical)
    kupiec_result = kupiec_test(violations, confidence_level)
    independence_result = christoffersen_independence_test(violations)
    conditional_result = christoffersen_conditional_coverage_test(
        violations,
        confidence_level,
    )

    print("Cálculo e Análise de Value at Risk e Expected Shortfall")
    print(f"Observações de retorno: {len(returns)}")
    print(f"Nível de confiança: {confidence_level:.0%}")
    print(f"VaR histórico: {historical:.4%}")
    print(f"VaR paramétrico normal: {parametric:.4%}")
    print(f"Expected Shortfall histórico: {historical_es:.4%}")
    print(f"Expected Shortfall paramétrico normal: {parametric_es:.4%}")
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


if __name__ == "__main__":
    main()
