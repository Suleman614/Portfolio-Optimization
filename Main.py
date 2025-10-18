import os
from pathlib import Path
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from fredapi import Fred
from scipy.optimize import minimize


def load_env(dotenv_path: str = ".env") -> None:
    """Populate os.environ with key/value pairs from a .env file if present."""
    env_file = Path(dotenv_path)
    if not env_file.exists():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip()

load_env()

# Define Tickers and Date Ranges
tickers = ['SPY','BND','GLD','QQQ','VTI']
end_date = datetime.today()
start_date = end_date - timedelta(days = 5*365)

# Download Adjusted Close Prices
# Adjusted because it accounts for dividends and stock splits and more accurately reflects the close price.
adj_close_df = pd.DataFrame()
for ticker in tickers:
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        progress=False,
        group_by='column',
        auto_adjust=False,
        actions=False,
    )
    if isinstance(data.columns, pd.MultiIndex):
        # Drop the ticker level if yfinance returns a (price, ticker) MultiIndex.
        level_names = list(data.columns.names)
        if 'Ticker' in level_names:
            data = data.droplevel('Ticker', axis=1)
        elif len(level_names) > 1:
            data = data.droplevel(-1, axis=1)
    if 'Adj Close' in data.columns:
        adj_close_df[ticker] = data['Adj Close']
    elif 'Adj Close' in getattr(data.columns, 'levels', [data.columns])[0]:
        # Handle cases where dropping the ticker level still leaves a named level.
        adj_close_df[ticker] = data.xs('Adj Close', axis=1, level=0)
    elif 'Close' in data.columns:
        adj_close_df[ticker] = data['Close']
    else:
        raise KeyError(f"'Adj Close' column not found for {ticker}. Available columns: {list(data.columns)}")
    
# Calculate Lognormal Returns
log_returns = np.log(adj_close_df / adj_close_df.shift(1))
log_returns = log_returns.dropna()

# Calculate Covariance Matrix, Measures Risk of the assets
cov_matrix = log_returns.cov() * 252

# Define Portfolio Performance Metrics throguh st dev, exp return, sharpe ratio (Return - Risk Free Rate / St Dev)

def standard_deviation(weights, cov_matrix):
    variance = weights.T @ cov_matrix @ weights
    return np.sqrt(variance)

def expected_return(weights, log_returns):
    return np.sum(log_returns.mean()*weights)*252

def sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    return (expected_return(weights, log_returns) - risk_free_rate) / standard_deviation(weights, cov_matrix)

# Set the Risk-Free Rate by using Federal Reserve API for 10 year treasury rates
fred_api_key = os.environ.get("FRED_API_KEY")
if not fred_api_key:
    raise RuntimeError(
        "FRED_API_KEY not found. Set it in the environment or create a local .env file."
    )
fred = Fred(api_key=fred_api_key)
ten_year_treasury_rate = fred.get_series_latest_release('GS10') / 100  # Convert percentage to decimal

if isinstance(ten_year_treasury_rate, pd.Series):
    risk_free_rate = ten_year_treasury_rate.iloc[-1]
else:
    risk_free_rate = float(ten_year_treasury_rate)

# Define the function to minimize (negative Sharpe Ratio)
def neg_sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate):
    return -sharpe_ratio(weights, log_returns, cov_matrix, risk_free_rate)

# Set up constraints and bounds for optimization
constraints = {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1}
bounds = [(0, 0.45) for _ in range(len(tickers))]
initial_weights = np.array([1/len(tickers)]*len(tickers))

# optimize the weights to maximize the Sharpe Ratio
optimized_results = minimize(neg_sharpe_ratio, initial_weights, args=(log_returns, cov_matrix, risk_free_rate), method='SLSQP', constraints=constraints, bounds=bounds) 
#'SLSQP' stands for Sequential Least Squares Quadratic Programming, which is a numerical optimization technique suitable for solving nonlinear optimization problems

# Get the optimial weights and Print Results
optimal_weights = optimized_results.x

print("Optimal Weights:")
for ticker, weight in zip(tickers, optimal_weights):
    print(f"{ticker}: {weight:.4f}")

optimal_portfolio_return = expected_return(optimal_weights, log_returns)
optimal_portfolio_volatility = standard_deviation(optimal_weights, cov_matrix)
optimal_sharpe_ratio = sharpe_ratio(optimal_weights, log_returns, cov_matrix, risk_free_rate)

print(f"Expected Annual Return: {optimal_portfolio_return:.4f}")
print(f"Expected Volatility: {optimal_portfolio_volatility:.4f}")
print(f"Sharpe Ratio: {optimal_sharpe_ratio:.4f}")

# Graphical Representation of the Optimal Portfolio
plt.figure(figsize=(10, 6))
plt.bar(tickers, optimal_weights)

plt.xlabel('Assets')
plt.ylabel('Optimal Weights')
plt.title('Optimal Portfolio Weights')

plt.show()
