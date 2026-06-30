import pandas as pd
import pytest

from src.returns import calculate_simple_returns


def test_calculate_simple_returns() -> None:
    prices = pd.Series([100.0, 110.0, 99.0])

    result = calculate_simple_returns(prices)

    expected = pd.Series([0.1, -0.1], index=[1, 2], name="simple_return")
    pd.testing.assert_series_equal(result, expected)


@pytest.mark.parametrize(
    "prices",
    [pd.Series(dtype=float), pd.Series([100.0]), pd.Series([None, 100.0])],
)
def test_calculate_simple_returns_rejects_insufficient_data(
    prices: pd.Series,
) -> None:
    with pytest.raises(ValueError):
        calculate_simple_returns(prices)


def test_calculate_simple_returns_rejects_non_series() -> None:
    with pytest.raises(TypeError):
        calculate_simple_returns([100.0, 101.0])  # type: ignore[arg-type]


def test_calculate_simple_returns_rejects_infinite_result() -> None:
    with pytest.raises(ValueError):
        calculate_simple_returns(pd.Series([0.0, 100.0]))
