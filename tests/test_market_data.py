import numpy as np
import pandas as pd
import pytest

from src.market_data import download_yahoo_prices


def test_download_yahoo_prices(monkeypatch: pytest.MonkeyPatch) -> None:
    index = pd.to_datetime(["2026-01-02", "2026-01-05", "2026-01-06"])
    response = pd.DataFrame({"Close": [30.0, np.nan, 31.5]}, index=index)
    captured_arguments = {}

    def fake_download(**kwargs):
        captured_arguments.update(kwargs)
        return response

    monkeypatch.setattr("src.market_data.yf.download", fake_download)

    result = download_yahoo_prices(" petr4.sa ", period="2Y")

    expected = pd.Series(
        [30.0, 31.5],
        index=index[[0, 2]],
        name="adjusted_close",
    )
    pd.testing.assert_series_equal(result, expected)
    assert captured_arguments["tickers"] == "PETR4.SA"
    assert captured_arguments["period"] == "2y"
    assert captured_arguments["auto_adjust"] is True
    assert captured_arguments["progress"] is False
    assert captured_arguments["threads"] is False


def test_download_yahoo_prices_handles_multi_level_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    columns = pd.MultiIndex.from_tuples([("Close", "AAPL")])
    response = pd.DataFrame([[100.0], [101.0]], columns=columns)
    monkeypatch.setattr(
        "src.market_data.yf.download",
        lambda **kwargs: response,
    )

    result = download_yahoo_prices("AAPL", period="1y")

    assert result.tolist() == [100.0, 101.0]


@pytest.mark.parametrize(
    ("ticker", "period", "exception"),
    [
        ("", "1y", ValueError),
        ("AAPL", "", ValueError),
        (123, "1y", TypeError),
        ("AAPL", 12, TypeError),
    ],
)
def test_download_yahoo_prices_rejects_invalid_parameters(
    ticker,
    period,
    exception,
) -> None:
    with pytest.raises(exception):
        download_yahoo_prices(ticker, period)


def test_download_yahoo_prices_rejects_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "src.market_data.yf.download",
        lambda **kwargs: pd.DataFrame(),
    )

    with pytest.raises(ValueError, match="no price data"):
        download_yahoo_prices("UNKNOWN", period="1y")


def test_download_yahoo_prices_rejects_missing_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = pd.DataFrame({"Open": [10.0, 11.0]})
    monkeypatch.setattr("src.market_data.yf.download", lambda **kwargs: response)

    with pytest.raises(ValueError, match="closing prices"):
        download_yahoo_prices("AAPL")


def test_download_yahoo_prices_wraps_download_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def raise_connection_error(**kwargs):
        raise ConnectionError("network unavailable")

    monkeypatch.setattr("src.market_data.yf.download", raise_connection_error)

    with pytest.raises(RuntimeError, match="failed to download"):
        download_yahoo_prices("AAPL")
