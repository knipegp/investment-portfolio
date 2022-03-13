"""Just some basic testing here"""
import argparse
import dataclasses
import typing

import pandas
import pypfopt
import requests_cache
import yaml
import yfinance
from pypfopt import expected_returns, objective_functions

from investment_portfolio.schema import PortfolioParams, PortfolioSchema


@dataclasses.dataclass
class _args:

    config: PortfolioParams


def parseargs() -> _args:
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", type=str, help="Path for the configuration file")
    args = parser.parse_args()
    conf = PortfolioSchema()
    with open(args.config_path) as config_file:
        conf = conf.dump(yaml.full_load(config_file.read()))
    return _args(conf)


def _get_price_history(
    ticker_symbols: typing.List[str], period: str, interval: str
) -> pandas.DataFrame:
    yfinance_cache = requests_cache.CachedSession("yfinance.cache")
    tickers: typing.Dict[str, yfinance.Ticker] = {
        ticker_name: yfinance.Ticker(ticker_name, session=yfinance_cache)
        for ticker_name in ticker_symbols
    }
    closing_history = pandas.DataFrame({"Date": []})
    closing_history.set_index("Date", inplace=True)
    for ticker_name, ticker in tickers.items():
        closing_history[ticker_name] = pandas.Series(
            pandas.DataFrame(
                ticker.history(
                    period=period,
                    interval=interval,
                )
            ).get("Close")
        )
    return closing_history


def main():
    args = parseargs()
    closing_history = _get_price_history(
        args.config.ticker_symbols,
        args.config.price_history.period,
        args.config.price_history.interval,
    )
    expected_returns_mu = pandas.Series(
        expected_returns.mean_historical_return(closing_history)
    )
    cov_mat_S = pandas.DataFrame(
        pypfopt.risk_models.CovarianceShrinkage(closing_history).ledoit_wolf()
    )
    ef = pypfopt.efficient_frontier.EfficientFrontier(expected_returns_mu, cov_mat_S)
    ef.add_objective(objective_functions.L2_reg, gamma=1)
    ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    print(cleaned_weights)
    ef.portfolio_performance(verbose=True)
