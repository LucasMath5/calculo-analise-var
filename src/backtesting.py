"""Funções simples para backtesting de Value at Risk."""

import math

import numpy as np
import pandas as pd


def count_var_violations(realized_returns: pd.Series, var_value: float) -> int:
    """Conta os dias em que a perda realizada excedeu o VaR.

    Como perdas são representadas por retornos negativos, há violação quando
    o retorno realizado é estritamente menor que ``-var_value``.

    Args:
        realized_returns: Série de retornos realizados.
        var_value: VaR não negativo, expresso na mesma escala dos retornos.

    Returns:
        Número de violações observadas.

    Raises:
        TypeError: Se as entradas não tiverem os tipos esperados.
        ValueError: Se os retornos estiverem vazios ou o VaR for inválido.
    """
    if not isinstance(realized_returns, pd.Series):
        raise TypeError("realized_returns must be a pandas Series")
    if isinstance(var_value, bool) or not isinstance(var_value, (int, float)):
        raise TypeError("var_value must be numeric")
    if not math.isfinite(var_value) or var_value < 0:
        raise ValueError("var_value must be a finite, non-negative number")

    try:
        clean_returns = (
            pd.to_numeric(realized_returns, errors="raise").dropna().astype(float)
        )
    except (TypeError, ValueError) as exc:
        raise TypeError("realized_returns must contain only numeric values") from exc

    if clean_returns.empty:
        raise ValueError("realized_returns must not be empty")
    if not np.isfinite(clean_returns.to_numpy()).all():
        raise ValueError("realized_returns must contain only finite values")

    return int((clean_returns < -var_value).sum())
