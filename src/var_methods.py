"""Métodos básicos de cálculo de Value at Risk e Expected Shortfall."""

import numpy as np
import pandas as pd
from scipy.stats import norm


def _validate_confidence_level(confidence_level: float) -> None:
    if isinstance(confidence_level, bool) or not isinstance(
        confidence_level, (int, float)
    ):
        raise TypeError("confidence_level must be numeric")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")


def _clean_returns(returns: pd.Series) -> pd.Series:
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")

    try:
        clean_returns = pd.to_numeric(returns, errors="raise").dropna().astype(float)
    except (TypeError, ValueError) as exc:
        raise TypeError("returns must contain only numeric values") from exc

    if clean_returns.empty:
        raise ValueError("returns must not be empty")
    if not np.isfinite(clean_returns.to_numpy()).all():
        raise ValueError("returns must contain only finite values")

    return clean_returns


def historical_var(
    returns: pd.Series, confidence_level: float = 0.95
) -> float:
    """Calcula o VaR histórico de uma série de retornos.

    Args:
        returns: Série de retornos observados.
        confidence_level: Nível de confiança entre zero e um.

    Returns:
        VaR como valor não negativo, representando a perda potencial.
    """
    _validate_confidence_level(confidence_level)
    clean_returns = _clean_returns(returns)
    lower_quantile = clean_returns.quantile(1 - confidence_level)
    return float(max(0.0, -lower_quantile))


def normal_parametric_var(
    returns: pd.Series, confidence_level: float = 0.95
) -> float:
    """Calcula o VaR paramétrico assumindo retornos normalmente distribuídos.

    A média e o desvio-padrão amostral são estimados a partir dos retornos.

    Args:
        returns: Série de retornos observados.
        confidence_level: Nível de confiança entre zero e um.

    Returns:
        VaR como valor não negativo, representando a perda potencial.

    Raises:
        ValueError: Se houver menos de dois retornos válidos.
    """
    _validate_confidence_level(confidence_level)
    clean_returns = _clean_returns(returns)
    if len(clean_returns) < 2:
        raise ValueError("at least two returns are required for parametric VaR")

    mean_return = clean_returns.mean()
    standard_deviation = clean_returns.std(ddof=1)
    lower_quantile = mean_return + norm.ppf(1 - confidence_level) * standard_deviation
    return float(max(0.0, -lower_quantile))


def historical_expected_shortfall(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    """Calcula o Expected Shortfall histórico de uma série de retornos.

    O método calcula a média dos retornos iguais ou inferiores ao quantil usado
    pelo VaR histórico. O sinal é invertido para representar a perda média da
    cauda como valor não negativo.

    Args:
        returns: Série de retornos observados.
        confidence_level: Nível de confiança entre zero e um.

    Returns:
        Expected Shortfall como valor não negativo.
    """
    _validate_confidence_level(confidence_level)
    clean_returns = _clean_returns(returns)
    lower_quantile = clean_returns.quantile(1 - confidence_level)
    tail_returns = clean_returns[clean_returns <= lower_quantile]
    return float(max(0.0, -tail_returns.mean()))


def normal_parametric_expected_shortfall(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    """Calcula o Expected Shortfall sob a hipótese de normalidade.

    A média da cauda inferior normal é obtida analiticamente a partir da média e
    do desvio-padrão amostral dos retornos.

    Args:
        returns: Série de retornos observados.
        confidence_level: Nível de confiança entre zero e um.

    Returns:
        Expected Shortfall como valor não negativo.

    Raises:
        ValueError: Se houver menos de dois retornos válidos.
    """
    _validate_confidence_level(confidence_level)
    clean_returns = _clean_returns(returns)
    if len(clean_returns) < 2:
        raise ValueError("at least two returns are required for parametric ES")

    tail_probability = 1 - confidence_level
    z_score = norm.ppf(tail_probability)
    mean_return = clean_returns.mean()
    standard_deviation = clean_returns.std(ddof=1)
    expected_tail_return = (
        mean_return
        - standard_deviation * norm.pdf(z_score) / tail_probability
    )
    return float(max(0.0, -expected_tail_return))
