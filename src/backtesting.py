"""Ferramentas para backtesting de Value at Risk."""

import math
from numbers import Real

import numpy as np
import pandas as pd
from scipy.special import xlog1py, xlogy
from scipy.stats import chi2

BacktestResult = dict[str, float | int | bool]


def _validate_probability(value: float, parameter_name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{parameter_name} must be numeric")
    if not 0 < value < 1:
        raise ValueError(f"{parameter_name} must be between 0 and 1")


def _validate_var_value(var_value: float) -> None:
    if isinstance(var_value, bool) or not isinstance(var_value, Real):
        raise TypeError("var_value must be numeric")
    if not math.isfinite(var_value) or var_value < 0:
        raise ValueError("var_value must be a finite, non-negative number")


def _validate_realized_returns(realized_returns: pd.Series) -> pd.Series:
    if not isinstance(realized_returns, pd.Series):
        raise TypeError("realized_returns must be a pandas Series")
    if realized_returns.empty:
        raise ValueError("realized_returns must not be empty")
    if realized_returns.isna().any():
        raise ValueError("realized_returns must not contain missing values")

    try:
        clean_returns = pd.to_numeric(realized_returns, errors="raise").astype(float)
    except (TypeError, ValueError) as exc:
        raise TypeError("realized_returns must contain only numeric values") from exc

    if not np.isfinite(clean_returns.to_numpy()).all():
        raise ValueError("realized_returns must contain only finite values")
    return clean_returns


def _validate_violations(violations: pd.Series) -> pd.Series:
    if not isinstance(violations, pd.Series):
        raise TypeError("violations must be a pandas Series")
    if violations.empty:
        raise ValueError("violations must not be empty")
    if violations.isna().any():
        raise ValueError("violations must not contain missing values")

    try:
        numeric_violations = pd.to_numeric(violations, errors="raise")
    except (TypeError, ValueError) as exc:
        raise TypeError("violations must contain only binary values") from exc

    if not numeric_violations.isin([0, 1]).all():
        raise ValueError("violations must contain only 0 and 1")
    return numeric_violations.astype(int)


def _bernoulli_log_likelihood(
    successes: int,
    observations: int,
    probability: float,
) -> float:
    failures = observations - successes
    return float(
        xlogy(successes, probability) + xlog1py(failures, -probability)
    )


def calculate_var_violations(
    realized_returns: pd.Series,
    var_value: float,
) -> pd.Series:
    """Identifica os dias em que a perda realizada excedeu o VaR.

    Como retornos negativos representam perdas, há violação quando o retorno
    realizado é estritamente menor que ``-var_value``.

    Args:
        realized_returns: Série cronológica de retornos realizados.
        var_value: VaR não negativo, na mesma escala dos retornos.

    Returns:
        Série inteira com ``1`` para violações e ``0`` para os demais dias.
    """
    clean_returns = _validate_realized_returns(realized_returns)
    _validate_var_value(var_value)

    violations = (clean_returns < -var_value).astype(int)
    violations.name = "var_violation"
    return violations


def count_var_violations(realized_returns: pd.Series, var_value: float) -> int:
    """Conta os dias em que a perda realizada excedeu o VaR."""
    return int(calculate_var_violations(realized_returns, var_value).sum())


def kupiec_test(
    violations: pd.Series,
    confidence_level: float = 0.95,
    significance_level: float = 0.05,
) -> BacktestResult:
    """Executa o teste de cobertura incondicional de Kupiec.

    A hipótese nula afirma que a frequência de violações é igual a
    ``1 - confidence_level``. A estatística de razão de verossimilhança segue
    assintoticamente uma distribuição qui-quadrado com um grau de liberdade.

    Args:
        violations: Série cronológica binária, com ``1`` para violações.
        confidence_level: Nível de confiança usado no cálculo do VaR.
        significance_level: Nível usado para decidir a rejeição da hipótese nula.

    Returns:
        Dicionário com estatística, p-valor, decisão e frequências observadas.
    """
    clean_violations = _validate_violations(violations)
    _validate_probability(confidence_level, "confidence_level")
    _validate_probability(significance_level, "significance_level")

    observations = len(clean_violations)
    violation_count = int(clean_violations.sum())
    expected_rate = 1 - confidence_level
    observed_rate = violation_count / observations

    null_log_likelihood = _bernoulli_log_likelihood(
        violation_count,
        observations,
        expected_rate,
    )
    alternative_log_likelihood = _bernoulli_log_likelihood(
        violation_count,
        observations,
        observed_rate,
    )
    statistic = max(
        0.0,
        -2 * (null_log_likelihood - alternative_log_likelihood),
    )
    p_value = float(chi2.sf(statistic, df=1))

    return {
        "statistic": statistic,
        "p_value": p_value,
        "reject_null": p_value < significance_level,
        "observations": observations,
        "violations": violation_count,
        "expected_rate": expected_rate,
        "observed_rate": observed_rate,
    }


def christoffersen_independence_test(
    violations: pd.Series,
    significance_level: float = 0.05,
) -> BacktestResult:
    """Testa a independência temporal das violações de VaR.

    O teste compara uma sequência de violações independentes com uma cadeia de
    Markov de primeira ordem. Sua estatística segue assintoticamente uma
    distribuição qui-quadrado com um grau de liberdade.

    Args:
        violations: Série cronológica binária, com ``1`` para violações.
        significance_level: Nível usado para decidir a rejeição da hipótese nula.

    Returns:
        Dicionário com estatística, p-valor, decisão e contagens de transição.
    """
    clean_violations = _validate_violations(violations)
    _validate_probability(significance_level, "significance_level")
    if len(clean_violations) < 2:
        raise ValueError("at least two observations are required")

    previous = clean_violations.iloc[:-1].to_numpy()
    current = clean_violations.iloc[1:].to_numpy()

    n00 = int(((previous == 0) & (current == 0)).sum())
    n01 = int(((previous == 0) & (current == 1)).sum())
    n10 = int(((previous == 1) & (current == 0)).sum())
    n11 = int(((previous == 1) & (current == 1)).sum())

    transitions = n00 + n01 + n10 + n11
    unconditional_probability = (n01 + n11) / transitions
    probability_01 = n01 / (n00 + n01) if n00 + n01 else 0.0
    probability_11 = n11 / (n10 + n11) if n10 + n11 else 0.0

    independent_log_likelihood = _bernoulli_log_likelihood(
        n01 + n11,
        transitions,
        unconditional_probability,
    )
    markov_log_likelihood = _bernoulli_log_likelihood(
        n01,
        n00 + n01,
        probability_01,
    ) + _bernoulli_log_likelihood(
        n11,
        n10 + n11,
        probability_11,
    )
    statistic = max(
        0.0,
        -2 * (independent_log_likelihood - markov_log_likelihood),
    )
    p_value = float(chi2.sf(statistic, df=1))

    return {
        "statistic": statistic,
        "p_value": p_value,
        "reject_null": p_value < significance_level,
        "transitions": transitions,
        "n00": n00,
        "n01": n01,
        "n10": n10,
        "n11": n11,
    }


def christoffersen_conditional_coverage_test(
    violations: pd.Series,
    confidence_level: float = 0.95,
    significance_level: float = 0.05,
) -> BacktestResult:
    """Testa conjuntamente cobertura correta e independência das violações.

    A estatística de cobertura condicional é a soma das estatísticas de Kupiec e
    de independência de Christoffersen e segue assintoticamente uma distribuição
    qui-quadrado com dois graus de liberdade.

    Args:
        violations: Série cronológica binária, com ``1`` para violações.
        confidence_level: Nível de confiança usado no cálculo do VaR.
        significance_level: Nível usado para decidir a rejeição da hipótese nula.

    Returns:
        Dicionário com as estatísticas componentes, estatística conjunta e decisão.
    """
    kupiec_result = kupiec_test(
        violations,
        confidence_level=confidence_level,
        significance_level=significance_level,
    )
    independence_result = christoffersen_independence_test(
        violations,
        significance_level=significance_level,
    )

    kupiec_statistic = float(kupiec_result["statistic"])
    independence_statistic = float(independence_result["statistic"])
    statistic = kupiec_statistic + independence_statistic
    p_value = float(chi2.sf(statistic, df=2))

    return {
        "statistic": statistic,
        "p_value": p_value,
        "reject_null": p_value < significance_level,
        "kupiec_statistic": kupiec_statistic,
        "independence_statistic": independence_statistic,
    }
