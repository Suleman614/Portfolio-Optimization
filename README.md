# Portfolio-Optimization

# Portfolio Optimization (Modern Portfolio Theory)

Portfolio optimization is a mathematical approach to constructing an investment portfolio that maximizes expected returns for a given level of risk.

This project demonstrates how to use **Modern Portfolio Theory (MPT)** to optimize a portfolio of stocks by calculating **optimal weights** that **maximize the Sharpe ratio** — providing the highest possible **risk-adjusted return**.  
The script downloads historical price data using `yfinance`, computes log returns and a covariance matrix, performs optimization using `scipy.optimize.minimize`, and visualizes the resulting portfolio weights.

---

## Features
- Downloads historical data using **yfinance**
- Computes **log returns** and the **covariance matrix**
- Maximizes **Sharpe ratio** under standard portfolio constraints
- Supports **optional FRED API** for real risk-free rate data
- Displays a **bar chart** of optimal portfolio weights using Matplotlib

---

## Installation

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt 
```

Optional: FRED API Key

If you want the script to pull a risk free rate directly from the Federal Reserve (FRED):
 1. Get a free API key from the Federal Reserve Economic Data (FRED) website.[<FRED website>](<https://fred.stlouisfed.org/docs/api/api_key.html>)
 2. Create a .env file in the same directory as your script and add the line below:
FRED_API_KEY=YOUR_FRED_KEY_HERE

If you don’t have an API key, the script will instead use a fixed risk free rate that you can modify directly in Main.py

Run the script with:
python3 Main.py
You’ll see console output displaying:
Expected Annual Return
Expected Volatility
Sharpe Ratio
A Matplotlib window will also open, showing the optimal weights for each ticker in your portfolio.

Configuration
Open Main.py and adjust the following parameters as needed:
# Example tickers
tickers = ['SPY', 'BND', 'GLD', 'QQQ', 'VTI']

# Date range (past 5 years)
end_date = datetime.today()
start_date = end_date - timedelta(days=5*365)

# Risk-free rate (only used if no FRED key)
risk_free_rate = 0.02 

# How It Works
Data Retrieval:
Historical adjusted close prices are downloaded using yfinance.
The script handles potential MultiIndex column formatting issues.
Log Returns:
Calculates continuous returns:

rt​ = ln(Pt/1Pt-1​​)

Statistics Calculation:
Computes expected returns and covariance matrix from historical data.
Optimization:
Uses scipy.optimize.minimize to maximize the Sharpe ratio
subject to the constraint that the sum of weights equals 1.
Visualization:
Displays a bar chart showing the optimized portfolio weights.

# Output Example

Console Output:
Expected Annual Return: 11.3%
Expected Volatility: 7.8%
Sharpe Ratio: 1.45

Chart:
A bar chart displaying each asset’s allocation percentage.

# Notes:
If you encounter KeyError: 'Adj Close', yfinance may have returned MultiIndex columns — the script already includes logic to handle that.
Ensure you have an active internet connection when downloading data from Yahoo Finance.
The FRED API key is optional but recommended for real risk-free rates.

License
This project is intended for educational purposes only.
Use at your own risk.
