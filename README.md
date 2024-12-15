# MACD Algorithm Trading Strategy

This repository implements an **MACD Algorithm Trading Strategy** built in Python. The strategy is designed to improve trading decision accuracy by adding an additional lower bound on the difference between each MACD peak and price, helping to control trading frequency and enhance the success rate. Additionally, the strategy incorporates **Average True Range (ATR)** to dynamically manage stop-profit and stop-loss levels.


<img src="https://github.com/user-attachments/assets/ff5eed5d-e7cc-45fa-ba4d-b2f8f8129bc0" alt="image" width="600"/>


The project uses:
- **Futu API** for real-time market data retrieval, backtesting, and order execution in the Hong Kong stock market.
- **QuantConnect** for backtesting U.S. stocks and cryptocurrencies, with advanced optimization features.
- **TradingView** for visualizing trading signals and technical indicators.

## Features
- **MACD Divergence Strategy**: Implements the core strategy for detecting divergence between price and MACD.
- **ATR-Based Stop Loss/Profit**: Uses **(ATR)** to calculate dynamic stop-loss and take-profit levels.
- **Backtesting**: Uses Futu API and QuantConnect to backtest the strategy.
- **Real-time Trading**: Executes orders using Futu API based on the trading strategy.
- **Visualization**: Trading signals and MACD indicators are visualized using TradingView.

## Files
- **`TradingStrategy.py`**: Execute the MACD trading strategy.
- **`FutuBackTest.py`**: Handles the backtesting process and integrates the trading strategy with Futu API.
- **`FutuFetchingData.py`**: Fetches historical data using the Futu API, used by `FutuBackTest.py` for backtesting.
- **`QuantConnect/`**: Contains files for running the strategy on QuantConnect:
  - **`main.py`**: The entry point for running the strategy on QuantConnect.
  - **`macd_atr_strategy.py`**: Implements the MACD strategy with ATR-based stop-loss and take-profit levels. This file is called by `main.py` to execute the strategy on QuantConnect.
- **`TradingView/MACD/`**: Contains a TradingView Pine Script for visualizing the strategy on TradingView:
  - **`MACD_with_ATR_Trading_Strategy.pine`**: A Pine Script strategy to visualize the MACD divergence strategy and ATR-based stop-loss/take-profit levels directly on TradingView.

## How the Strategy Works  
The **MACD Divergence Strategy** identifies divergence between the price of an asset and the MACD indicator. The program detects MACD peaks and introduces a minimum difference threshold between the MACD peak and the price, which helps reduce trade frequency and enhances the strategy's success rate.

Additionally, the strategy incorporates **(ATR)** to dynamically adjust stop-loss and take-profit levels based on market volatility, providing more flexibility in different market conditions.

The **FutuBackTest** feature allows users to conduct a detailed review of the portfolio performance, including key metrics such as:
- **Strategy Return (%)**: The overall return of the strategy.
- **Total Trades**: The number of trades executed.
- **Percent Profitable**: The percentage of profitable trades.
- **Risk-Reward Ratio**: Displays the ratio of risk to reward, helping to assess the potential return relative to the risk taken.
- **Winning and Losing Trades**: Number of trades that resulted in profit or loss.
- **Average Winning/Losing Trades Return**: The average return of winning and losing trades, respectively.
- **Average Return per Trade (%)**: The average return per trade, helping to evaluate consistency.
- **Largest Winning and Losing Trade (%)**: The largest percentage gain or loss in a single trade.
- **Max Consecutive Wins/Losses**: The maximum streak of consecutive winning or losing trades, useful for understanding trade patterns.
- **Max Consecutive Win/Loss Return (%)**: The return associated with the longest streak of consecutive wins or losses.

These metrics allow for a comprehensive performance analysis, including a **comparison with the Hang Seng Index (HSI)**, enabling users to evaluate how well the strategy performs relative to the market benchmark.

## Environment Setup

This project is developed using **Python 3.8**. To set up the environment, you need to install the following Python packages:

- `numpy`
- `pandas`
- `matplotlib.pyplot`
- `talib`
- `futu`

## Set Up Futu API

1. Download and Install **Futu OpenD** (the gateway program of Futu API) from the following documentation: https://openapi.futunn.com/futu-api-doc/en/
2. Before starting the program, initialize Futu OpenD and log in.
3. Ensure that you change the host and port number in the FutuFetchingData.py file to match your setup. This is essential for connecting to the Futu API.
