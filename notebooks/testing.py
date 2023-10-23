# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---
# %% [markdown]
# Walking through the example [here](https://pyportfolioopt.readthedocs.io/en/latest/UserGuide.html#user-guide) with some randomly chosen tickers.
# %%
import pypfopt
from pypfopt import expected_returns
from pypfopt import objective_functions

from investment_portfolio import get_price_history


closing_history = get_price_history(
    ("NFLX", "GOOG", "SPOT", "AMD", "NVDA", "INTC", "ARM", "SONY", "ADI", "TXN", "DIS"),
    "5y",
    "1d",
)
expected_returns_mu = expected_returns.mean_historical_return(closing_history)
cov_mat_s = pypfopt.risk_models.CovarianceShrinkage(closing_history).ledoit_wolf()
ef = pypfopt.efficient_frontier.EfficientFrontier(expected_returns_mu, cov_mat_s)
ef.add_objective(objective_functions.L2_reg, gamma=1)
ef.max_sharpe()

# %%
ef.portfolio_performance(verbose=True)

# %% [markdown]
# This portfolio does not have a great return given the risk. Leads to a low Sharpe ratio. Volotility is very high.

# %%
from matplotlib import pyplot
from pypfopt import plotting

fig, ax = pyplot.subplots()
plotting.plot_efficient_frontier(ef, ax=ax, show_assets=True)
pyplot.show()

# %% [markdown]
# This is broken. Might want to submit a PR. See [link](https://github.com/robertmartin8/PyPortfolioOpt/issues/562).
