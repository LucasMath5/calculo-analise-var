"""Funções para cálculo de retornos financeiros."""

import numpy as np
import pandas as pd


def calculate_simple_returns(prices: pd.Series) -> pd.Series:
    """Calcula retornos simples a partir de uma série de preços.

    O retorno simples no instante ``t`` é calculado como
    ``preço_t / preço_(t-1) - 1``. Valores nulos gerados pelo cálculo são
    removidos.

    Args:
        prices: Série pandas com pelo menos dois preços numéricos não nulos.

    Returns:
        Série com os retornos simples.

    Raises:
        TypeError: Se ``prices`` não for uma ``pandas.Series`` ou contiver
            valores não numéricos.
        ValueError: Se não houver dados suficientes ou o cálculo produzir
            retornos não finitos.
    """
    if not isinstance(prices, pd.Series):
        raise TypeError("prices must be a pandas Series")

    try:
        numeric_prices = pd.to_numeric(prices, errors="raise").astype(float)
    except (TypeError, ValueError) as exc:
        raise TypeError("prices must contain only numeric values") from exc

    if numeric_prices.notna().sum() < 2:
        raise ValueError("at least two non-null prices are required")

    returns = numeric_prices.pct_change(fill_method=None).dropna()
    if returns.empty:
        raise ValueError("prices do not contain consecutive observations")
    if not np.isfinite(returns.to_numpy()).all():
        raise ValueError("prices produced non-finite returns")

    returns.name = "simple_return"
    return returns
