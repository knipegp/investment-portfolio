"""Portfolio utilities."""
from __future__ import annotations

import typing

import pandas
import pyrate_limiter
import requests
import requests_cache
import requests_ratelimiter
import yfinance
from loguru import logger
from requests_cache.backends import sqlite


class _CachedRateLimitedSessionCore(
    requests_cache.CacheMixin, requests_ratelimiter.LimiterMixin, requests.Session
):
    """Custom :mod:`yfinance` session using a cache and a rate limiter.

    .. example::

        https://requests-ratelimiter.readthedocs.io/en/stable/#custom-session-example-requests-cache

    .. example::

        https://github.com/ranaroussi/yfinance#smarter-scraping
    """

    @classmethod
    def with_defaults(cls) -> _CachedRateLimitedSessionCore:
        """Create a new instance with defaults caching and limiting behavior.

        :returns: New instance
        """
        return cls(
            limiter=pyrate_limiter.Limiter(
                pyrate_limiter.RequestRate(
                    limit=2, interval=pyrate_limiter.Duration.SECOND * 5
                )
            ),
            bucket_class=requests_ratelimiter.MemoryQueueBucket,
            backend=sqlite.SQLiteCache("yfinance.cache"),
        )

    def __getstate__(self) -> typing.NoReturn:
        raise NotImplementedError()


class RequestsSessionError(Exception):
    """Raised when the :class:`requests.Session` encounters an unexpected
    error."""


class CachedRateLimitedSession:  # pylint: disable=too-few-public-methods
    """Session wrapper ensuring that only one session is created per
    application."""

    _instance: typing.ClassVar[_CachedRateLimitedSessionCore | None] = None

    def __init__(self) -> None:
        if CachedRateLimitedSession._instance is None:
            CachedRateLimitedSession._instance = (
                _CachedRateLimitedSessionCore.with_defaults()
            )

    @property
    def core(self) -> _CachedRateLimitedSessionCore:
        """Retrieve the session core.

        :raises RequestsSessionError: Session core is not initialized
        :returns: Session core
        """
        if CachedRateLimitedSession._instance is None:
            raise RequestsSessionError("No requests session exists")
        return CachedRateLimitedSession._instance


def get_price_history(
    ticker_symbols: typing.Sequence[str], period: str, interval: str
) -> pandas.DataFrame:
    """Retrieve the closing price history for the given tickers.

    :param ticker_symbols: List of ticker names for which data is
        collected
    :param period: Time since now the prices will be collected
    :param interval: Time between prices
    :returns: Historical closing prices
    """
    session = CachedRateLimitedSession()
    tickers: typing.Dict[str, yfinance.Ticker] = {
        ticker_name: yfinance.Ticker(ticker_name, session=session.core)
        for ticker_name in ticker_symbols
    }
    closing_history = pandas.DataFrame({"Date": []})
    closing_history.set_index("Date", inplace=True)
    for ticker_name, ticker in tickers.items():
        logger.info(
            f"Retrieving closing prices {ticker_name}, period {period}, interval {interval}"
        )
        closing_history[ticker_name] = ticker.history(
            period=period,
            interval=interval,
        )["Close"]
    return closing_history
