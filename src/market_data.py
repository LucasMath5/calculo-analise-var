"""Integrações para obtenção de dados de mercado."""

import numpy as np
import pandas as pd
import yfinance as yf


def download_yahoo_prices(
    ticker: str,
    period: str = "2y",
) -> pd.Series:
    """Baixa preços diários ajustados de um ativo pelo Yahoo Finance.

    A função usa o fechamento retornado pelo ``yfinance`` com
    ``auto_adjust=True``, portanto os preços são ajustados por eventos como
    dividendos e desdobramentos.

    Args:
        ticker: Símbolo reconhecido pelo Yahoo Finance, como ``AAPL`` ou
            ``PETR4.SA``.
        period: Período aceito pelo ``yfinance``, como ``6mo``, ``1y``, ``2y``
            ou ``5y``.

    Returns:
        Série cronológica de preços de fechamento ajustados.

    Raises:
        TypeError: Se ``ticker`` ou ``period`` não forem strings.
        ValueError: Se os parâmetros forem vazios ou não houver preços válidos.
        RuntimeError: Se a consulta ao Yahoo Finance falhar.
    """
    if not isinstance(ticker, str):
        raise TypeError("ticker must be a string")
    if not isinstance(period, str):
        raise TypeError("period must be a string")

    clean_ticker = ticker.strip().upper()
    clean_period = period.strip().lower()
    if not clean_ticker:
        raise ValueError("ticker must not be empty")
    if not clean_period:
        raise ValueError("period must not be empty")

    try:
        market_data = yf.download(
            tickers=clean_ticker,
            period=clean_period,
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
            timeout=10,
            multi_level_index=False,
        )
    except Exception as exc:
        raise RuntimeError(
            f"failed to download prices for {clean_ticker} from Yahoo Finance"
        ) from exc

    if market_data is None or market_data.empty:
        raise ValueError(f"no price data found for ticker {clean_ticker}")
    if "Close" not in market_data.columns:
        raise ValueError("Yahoo Finance response does not contain closing prices")

    closing_prices = market_data["Close"]
    if isinstance(closing_prices, pd.DataFrame):
        if clean_ticker in closing_prices.columns:
            closing_prices = closing_prices[clean_ticker]
        elif closing_prices.shape[1] == 1:
            closing_prices = closing_prices.iloc[:, 0]
        else:
            raise ValueError("could not identify the requested ticker in response")

    try:
        prices = pd.to_numeric(closing_prices, errors="raise").dropna().astype(float)
    except (TypeError, ValueError) as exc:
        raise ValueError("closing prices must be numeric") from exc

    if len(prices) < 2:
        raise ValueError("at least two valid closing prices are required")
    if not np.isfinite(prices.to_numpy()).all() or (prices <= 0).any():
        raise ValueError("closing prices must be finite and positive")

    prices.name = "adjusted_close"
    return prices.sort_index()
