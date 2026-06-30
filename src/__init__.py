"""Ferramentas básicas para cálculo e análise de Value at Risk."""

from .backtesting import count_var_violations
from .returns import calculate_simple_returns
from .var_methods import historical_var, normal_parametric_var

__all__ = [
    "calculate_simple_returns",
    "historical_var",
    "normal_parametric_var",
    "count_var_violations",
]
