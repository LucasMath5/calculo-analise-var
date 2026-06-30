import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from src.var_methods import historical_var, normal_parametric_var


def test_historical_var() -> None:
    returns = pd.Series([-0.10, -0.05, 0.00, 0.05, 0.10])

    result = historical_var(returns, confidence_level=0.80)

    assert result == pytest.approx(0.06)


def test_normal_parametric_var() -> None:
    returns = pd.Series([-0.02, -0.01, 0.00, 0.01, 0.02])
    expected = -(returns.mean() + norm.ppf(0.05) * returns.std(ddof=1))

    result = normal_parametric_var(returns, confidence_level=0.95)

    assert result == pytest.approx(expected)


@pytest.mark.parametrize("confidence_level", [0.0, 1.0, -0.1, 1.1])
def test_var_methods_reject_invalid_confidence_level(
    confidence_level: float,
) -> None:
    returns = pd.Series([-0.01, 0.01])

    with pytest.raises(ValueError):
        historical_var(returns, confidence_level)
    with pytest.raises(ValueError):
        normal_parametric_var(returns, confidence_level)


@pytest.mark.parametrize("method", [historical_var, normal_parametric_var])
def test_var_methods_reject_empty_returns(method) -> None:
    with pytest.raises(ValueError):
        method(pd.Series(dtype=float))


def test_normal_parametric_var_requires_two_returns() -> None:
    with pytest.raises(ValueError):
        normal_parametric_var(pd.Series([0.01]))


def test_var_is_never_negative() -> None:
    positive_returns = pd.Series([0.01, 0.02, 0.03])

    assert historical_var(positive_returns) == 0.0
    assert normal_parametric_var(positive_returns, confidence_level=0.50) == 0.0


def test_var_methods_reject_non_finite_returns() -> None:
    with pytest.raises(ValueError):
        historical_var(pd.Series([0.01, np.inf]))
