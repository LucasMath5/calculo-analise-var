"""Ferramentas básicas para cálculo e análise de Value at Risk."""

from .backtesting import (
    calculate_var_violations,
    christoffersen_conditional_coverage_test,
    christoffersen_independence_test,
    count_var_violations,
    kupiec_test,
)
from .market_data import download_yahoo_prices
from .returns import calculate_simple_returns
from .var_methods import historical_var, normal_parametric_var

__all__ = [
    "calculate_simple_returns",
    "historical_var",
    "normal_parametric_var",
    "calculate_var_violations",
    "count_var_violations",
    "kupiec_test",
    "christoffersen_independence_test",
    "christoffersen_conditional_coverage_test",
    "download_yahoo_prices",
]
