import numpy as np
import pandas as pd
import pytest
from scipy.stats import chi2

from src.backtesting import (
    calculate_var_violations,
    christoffersen_conditional_coverage_test,
    christoffersen_independence_test,
    count_var_violations,
    kupiec_test,
)


def test_calculate_var_violations() -> None:
    returns = pd.Series([-0.01, -0.03, -0.02, 0.01, -0.05])

    result = calculate_var_violations(returns, var_value=0.02)

    expected = pd.Series([0, 1, 0, 0, 1], name="var_violation")
    pd.testing.assert_series_equal(result, expected)


def test_count_var_violations() -> None:
    returns = pd.Series([-0.01, -0.03, -0.02, 0.01, -0.05])

    assert count_var_violations(returns, var_value=0.02) == 2


def test_return_equal_to_var_is_not_a_violation() -> None:
    assert count_var_violations(pd.Series([-0.02]), var_value=0.02) == 0


def test_kupiec_accepts_expected_violation_rate() -> None:
    violations = pd.Series([1] * 5 + [0] * 95)

    result = kupiec_test(violations, confidence_level=0.95)

    assert result["statistic"] == pytest.approx(0.0)
    assert result["p_value"] == pytest.approx(1.0)
    assert result["reject_null"] is False
    assert result["observed_rate"] == pytest.approx(0.05)


def test_kupiec_rejects_excessive_violations() -> None:
    violations = pd.Series([1] * 20 + [0] * 80)

    result = kupiec_test(violations, confidence_level=0.95)

    assert result["p_value"] < 0.05
    assert result["reject_null"] is True


def test_kupiec_handles_no_violations() -> None:
    result = kupiec_test(pd.Series([0] * 100), confidence_level=0.95)

    assert np.isfinite(result["statistic"])
    assert 0 <= result["p_value"] <= 1


def test_christoffersen_transition_counts() -> None:
    violations = pd.Series([0, 0, 1, 0, 1, 1])

    result = christoffersen_independence_test(violations)

    assert result["n00"] == 1
    assert result["n01"] == 2
    assert result["n10"] == 1
    assert result["n11"] == 1
    assert result["transitions"] == 5
    assert 0 <= result["p_value"] <= 1


def test_christoffersen_rejects_clustered_violations() -> None:
    violations = pd.Series([0] * 45 + [1] * 10 + [0] * 45)

    result = christoffersen_independence_test(violations)

    assert result["p_value"] < 0.05
    assert result["reject_null"] is True


def test_conditional_coverage_combines_statistics() -> None:
    violations = pd.Series([0] * 45 + [1] * 10 + [0] * 45)
    kupiec_result = kupiec_test(violations)
    independence_result = christoffersen_independence_test(violations)

    result = christoffersen_conditional_coverage_test(violations)

    expected_statistic = (
        kupiec_result["statistic"] + independence_result["statistic"]
    )
    assert result["statistic"] == pytest.approx(expected_statistic)
    assert result["p_value"] == pytest.approx(chi2.sf(expected_statistic, df=2))


@pytest.mark.parametrize("var_value", [-0.01, np.inf, np.nan])
def test_count_var_violations_rejects_invalid_var(var_value: float) -> None:
    with pytest.raises(ValueError):
        count_var_violations(pd.Series([-0.01]), var_value)


@pytest.mark.parametrize(
    "returns",
    [pd.Series(dtype=float), pd.Series([0.01, np.nan])],
)
def test_calculate_var_violations_rejects_invalid_returns(
    returns: pd.Series,
) -> None:
    with pytest.raises(ValueError):
        calculate_var_violations(returns, var_value=0.02)


def test_count_var_violations_rejects_non_series() -> None:
    with pytest.raises(TypeError):
        count_var_violations([-0.03], var_value=0.02)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "violations",
    [
        pd.Series(dtype=int),
        pd.Series([0, 2, 1]),
        pd.Series([0, np.nan, 1]),
    ],
)
@pytest.mark.parametrize(
    "test_function",
    [kupiec_test, christoffersen_independence_test],
)
def test_backtests_reject_invalid_violation_series(
    test_function,
    violations: pd.Series,
) -> None:
    with pytest.raises(ValueError):
        test_function(violations)


@pytest.mark.parametrize("confidence_level", [0.0, 1.0, -0.1, 1.1])
def test_kupiec_rejects_invalid_confidence_level(
    confidence_level: float,
) -> None:
    with pytest.raises(ValueError):
        kupiec_test(pd.Series([0, 1]), confidence_level=confidence_level)


@pytest.mark.parametrize("significance_level", [0.0, 1.0, -0.1, 1.1])
def test_backtests_reject_invalid_significance_level(
    significance_level: float,
) -> None:
    violations = pd.Series([0, 1])

    with pytest.raises(ValueError):
        kupiec_test(violations, significance_level=significance_level)
    with pytest.raises(ValueError):
        christoffersen_independence_test(
            violations,
            significance_level=significance_level,
        )


def test_christoffersen_requires_two_observations() -> None:
    with pytest.raises(ValueError):
        christoffersen_independence_test(pd.Series([0]))
