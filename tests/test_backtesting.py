import numpy as np
import pandas as pd
import pytest

from src.backtesting import count_var_violations


def test_count_var_violations() -> None:
    returns = pd.Series([-0.01, -0.03, -0.02, 0.01, -0.05])

    result = count_var_violations(returns, var_value=0.02)

    assert result == 2


def test_return_equal_to_var_is_not_a_violation() -> None:
    assert count_var_violations(pd.Series([-0.02]), var_value=0.02) == 0


@pytest.mark.parametrize("var_value", [-0.01, np.inf, np.nan])
def test_count_var_violations_rejects_invalid_var(var_value: float) -> None:
    with pytest.raises(ValueError):
        count_var_violations(pd.Series([-0.01]), var_value)


def test_count_var_violations_rejects_empty_returns() -> None:
    with pytest.raises(ValueError):
        count_var_violations(pd.Series(dtype=float), var_value=0.02)


def test_count_var_violations_rejects_non_series() -> None:
    with pytest.raises(TypeError):
        count_var_violations([-0.03], var_value=0.02)  # type: ignore[arg-type]
