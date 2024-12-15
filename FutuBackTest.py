import numpy as np
import pandas as pd
from TradingStrategy import MACDATRStrategy
import matplotlib.pyplot as plt
from FutuFetchingData import *
import os
import csv

class PortfolioManager:
    def __init__(self, initial_balance=100000):
        self.initial_balance = initial_balance
        self.account_balance = initial_balance
        self.positions = {}  # Store the active stock positions (max 2 stocks)
        self.max_positions = 2
        self.balance_history = []
        self.trade_history = []

        #for tracking
        self.winning_trades = 0
        self.losing_trades = 0
        self.winning_trades_return = 0
        self.losing_trades_return = 0

        self.consecutive_wins = 0
        self.consecutive_win_return = 1
        self.max_consecutive_win_return = 1
        self.max_consecutive_wins = 0

        self.consecutive_losses = 0
        self.max_consecutive_losses = 0
        self.consecutive_loss_return = 1
        self.max_consecutive_loss_return = 1

        self.largest_winning_trade = 0
        self.largest_losing_trade = 0

        self.portfolio_return = 1
        self.stock_trade_stats = {} # To track trades and returns per stock

    def can_buy(self, stock_symbol):
        return len(self.positions) < self.max_positions and self.account_balance > 1000 #and stock_symbol not in self.positions

    def buy_stock(self, stock_symbol, buy_price, stop_loss_price, stop_profit_target):
        if self.can_buy(stock_symbol):
            if len(self.positions) == 0:
                investment = self.account_balance * 0.5  # 50% of the total balance
                num_shares = investment // buy_price
                self.account_balance -= num_shares * buy_price

            # For the second buy signal (second stock), use 100% of the remaining balance
            elif len(self.positions) == 1:
                investment = self.account_balance  # Use all remaining balance
                num_shares = investment // buy_price
                self.account_balance -= num_shares * buy_price

            # Store the position with stock-specific details
            self.positions[stock_symbol] = {
                'num_shares': num_shares,
                'buy_price': buy_price,
                'stop_loss_price': stop_loss_price,
                'stop_profit_target': stop_profit_target
            }

            # Store the position with stock-specific details
            self.positions[stock_symbol] = {
                'num_shares': num_shares,
                'buy_price': buy_price,
                'stop_loss_price': stop_loss_price,
                'stop_profit_target': stop_profit_target
            }
            self.trade_history.append((stock_symbol, 'Buy', buy_price))

    def sell_stock(self, stock_symbol, sell_price):
        if stock_symbol in self.positions:
            position = self.positions[stock_symbol]
            num_shares = position['num_shares']
            profit = num_shares * (sell_price - position['buy_price'])
            current_portfolio_value = self.account_balance + sum(details['num_shares'] * details['buy_price'] for details in self.positions.values())
            percentage_profit = profit/current_portfolio_value * 100

            self.account_balance += num_shares * sell_price

            # Record the trade and remove the position
            self.trade_history.append((stock_symbol, 'Sell', sell_price))
            del self.positions[stock_symbol]

            # Track win/loss and profit for each trade
            self.track_trade_profit(stock_symbol, percentage_profit)

    def get_final_return(self):
        final_portfolio_value = self.account_balance
        for stock_symbol, details in self.positions.items():
            final_portfolio_value += details['num_shares'] * details['buy_price']
        return (final_portfolio_value - self.initial_balance) / self.initial_balance * 100


    def track_trade_profit(self, stock_symbol, percentage_profit):

        self.portfolio_return *= (1 + percentage_profit/100)
        # Track wins/losses
        if percentage_profit > 0:
            if self.consecutive_wins == 0: self.consecutive_win_return = 1
            self.winning_trades += 1
            self.winning_trades_return += percentage_profit

            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.consecutive_win_return *= (1 + percentage_profit / 100)


            # Update largest winning trade
            if percentage_profit > self.largest_winning_trade:
                self.largest_winning_trade = percentage_profit

            if self.consecutive_win_return > self.max_consecutive_win_return:
                self.max_consecutive_win_return = self.consecutive_win_return

            # Update max consecutive wins
            if self.consecutive_wins > self.max_consecutive_wins:
                self.max_consecutive_wins = self.consecutive_wins

        else:
            if self.consecutive_losses == 0: self.consecutive_loss_return = 1
            self.losing_trades += 1
            self.losing_trades_return += percentage_profit

            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.consecutive_loss_return *= (1 + percentage_profit/100)

            # Update largest losing trade
            if percentage_profit < self.largest_losing_trade:
                self.largest_losing_trade = percentage_profit

            if self.consecutive_loss_return < self.max_consecutive_loss_return:
                self.max_consecutive_loss_return = self.consecutive_loss_return

            # Update max consecutive losses
            if self.consecutive_losses > self.max_consecutive_losses:
                self.max_consecutive_losses = self.consecutive_losses

        # Track stock-specific performance
        self.track_stock_trade(stock_symbol, percentage_profit)

    def track_stock_trade(self, stock_symbol, percentage_profit):
        if stock_symbol not in self.stock_trade_stats:
            self.stock_trade_stats[stock_symbol] = {'trades': 0, 'return': 0}
        self.stock_trade_stats[stock_symbol]['trades'] += 1
        self.stock_trade_stats[stock_symbol]['return'] += percentage_profit

    def get_statistics(self):
        total_trades = len(self.trade_history) // 2  # Buy/Sell pairs
        percent_profitable = (self.winning_trades / total_trades) * 100 if total_trades > 0 else 0
        avg_return_per_trade = sum(stock['return'] for stock in self.stock_trade_stats.values()) / total_trades if total_trades > 0 else 0
        avg_return_winning = self.winning_trades_return / self.winning_trades
        avg_return_losing = self.losing_trades_return / self.losing_trades
        risk_reward_ratio = -avg_return_losing / avg_return_winning

        stats = {
            "Strategy Return (%)": f"{(self.portfolio_return - 1) * 100:.2f}",
            "Total Trades": total_trades,
            "Percent Profitable": f"{percent_profitable:.2f}",
            "Risk Reward Ratio":f"1:{(1 / risk_reward_ratio):.2f}",
            "Winning Trades": self.winning_trades,
            "Losing Trades": self.losing_trades,
            "Average Winning Trades Return": f"{avg_return_winning:.2f}",
            "Average Losing Trades Return": f"{avg_return_losing:.2f}",
            "Average Return per Trade (%)": f"{avg_return_per_trade:.2f}",
            "Largest Winning Trade (%)": f"{self.largest_winning_trade:.2f}",
            "Largest Losing Trade (%)": f"{self.largest_losing_trade:.2f}",
            "Max Consecutive Wins": self.max_consecutive_wins,
            "Max Consecutive Win Return (%)": f"{(self.max_consecutive_win_return - 1) * 100:.2f}",
            "Max Consecutive Losses": self.max_consecutive_losses,
            "Max Consecutive Loss Return (%)": f"{(self.max_consecutive_loss_return - 1) * 100:.2f}",
        }
        for key, value in stats.items():
            print(f"{key}: {value}")

        print("Stock Trade Stats:(stock), (trades), (return)")
        for stock_symbol, stock_data in self.stock_trade_stats.items():
            print(f"{stock_symbol},{stock_data['trades']},{stock_data['return']:.2f}")
        return
def stock_length_validation(stocks_data):
    lengths = {stock: len(stocks_data[stock]['Close']) for stock in stocks_data}

    # Find the most common length (the expected length)
    expected_length = max(set(lengths.values()), key=list(lengths.values()).count)

    # Identify stocks that don't match the expected length
    mismatched_stocks = {stock: length for stock, length in lengths.items() if length != expected_length}

    # If there are any mismatches, raise an error and print details
    if mismatched_stocks:
        print("The following stocks have differing lengths for 'Close' data:")
        for stock, length in mismatched_stocks.items():
            print(f"{stock}: Length = {length} (Expected = {expected_length})")
        raise ValueError("Mismatch in length of 'Close' data detected. Adjust the data before continuing.")
    return

def backtest_strategy(stocks_data):

    stock_length_validation(stocks_data)
    # Initialize portfolio manager with $10,000
    portfolio = PortfolioManager(initial_balance=100000)

    strategies = {stock: MACDATRStrategy() for stock in stocks_data.keys()}  # One strategy per stock

    for i in range(len(stocks_data[next(iter(stocks_data))]['Close'])):  # Loop through data points (assuming all stocks have same length)
        current_prices = {stock: stocks_data[stock]['Close'][i] for stock in stocks_data.keys()}

        # Update strategy signals for all stocks
        for stock, data in stocks_data.items():
            signal = strategies[stock].update(data['Close'][i], data['High'][i], data['Low'][i])

            if signal is None:
                continue

            if signal['signal'] == "Buy" and portfolio.can_buy(stock):
                portfolio.buy_stock(stock, signal['buy_price'], signal['stop_loss_price'], signal['stop_profit_target'])

            if signal['signal'] == "Sell":
                portfolio.sell_stock(stock, signal['sell_price'])

        #portfolio.update_portfolio(current_prices)
        portfolio_value = portfolio.account_balance
        for stock_symbol, details in portfolio.positions.items():
            portfolio_value += details['num_shares'] * current_prices.get(stock_symbol, details['buy_price'])
        portfolio.balance_history.append(portfolio_value)
    # Final return report
    portfolio.get_statistics()
    return portfolio.get_final_return(), portfolio.trade_history, portfolio.balance_history


# Example usage with fetched data from Futu OpenAPI
if __name__ == "__main__":
    #['HK.00700', 'HK.00388', 'HK.02318', 'HK.00939', 'HK.01299', 'HK.00883', 'HK.01211', 'HK.01398', 'HK.00941', 'HK.02020', 'HK.02628', 'HK.00005', 'HK.03988', 'HK.00857', 'HK.00291', 'HK.00175']
    #['HK.00005','HK.00700','HK.00016','HK.00002','HK.01038','HK.00941','HK.00992','HK.00883','HK.01177','HK.00027']
    #['HK.01398', 'HK.01177', 'HK.02628', 'HK.00175', 'HK.00883', 'HK.00291', 'HK.00005', 'HK.00002', 'HK.00027', 'HK.00700', 'HK.02318', 'HK.00992', 'HK.01299', 'HK.03988', 'HK.00941', 'HK.01211', 'HK.00016', 'HK.00857', 'HK.01038', 'HK.02020', 'HK.00388', 'HK.00939', 'HK.00883']
    stock_list = [
    'HK.01398', 'HK.01177', 'HK.02628', 'HK.00175', 'HK.00883', 'HK.00291',
    'HK.00005', 'HK.00002', 'HK.00027', 'HK.00700', 'HK.02318',
    'HK.01299', 'HK.03988', 'HK.00941', 'HK.01211', 'HK.00016',
    'HK.01038', 'HK.02020', 'HK.00388', 'HK.00939', 'HK.00883',
    'HK.00700', 'HK.00388', 'HK.00027', 'HK.00857', 'HK.00992',
    'HK.02318', 'HK.00939', 'HK.01398', 'HK.00857', 'HK.01299',
    'HK.00883', 'HK.01211', 'HK.00960', 'HK.03988', 'HK.02020',
    'HK.02628', 'HK.00941', 'HK.01109', 'HK.00688', 'HK.03968',

    ]
    stocks_data = {}

    for stock in stock_list:
        # Fetch data for each stock from Futu OpenAPI (pseudo-code, replace with actual API call)
        # data = fetch_futu_data(stock_code=stock, start_date='2014-01-01', end_date='2024-01-10', ktype='K_30M')
        data = fetch_futu_data(stock_code=stock, start_date='2019-10-16', end_date='2024-10-16', ktype='K_60M')
        if data is not None:
            stocks_data[stock] = process_futu_data(data)

    hsi_data = fetch_futu_data(stock_code='HK.02800', start_date='2019-10-16', end_date='2024-10-16', ktype='K_60M')

    if hsi_data is not None:
        hsi_data = process_futu_data(hsi_data)
        hsi_closes = hsi_data['Close']

    if stocks_data:
        # Run the backtest
        final_return, trades, balance_history = backtest_strategy(stocks_data)

        # Normalize portfolio balance and HSI to the same initial value for comparison
        portfolio_normalized = np.array(balance_history) / balance_history[0] * 100
        hsi_normalized = np.array(hsi_closes) / hsi_closes[0] * 100

        # Plot portfolio balance history
        plt.plot(portfolio_normalized, label="Portfolio Balance")

        # Plot HSI for comparison
        plt.plot(hsi_normalized, label="HSI (2800)", linestyle='--')

        # Plot formatting
        plt.title("Portfolio Balance vs HSI (2800) Over Time")
        plt.xlabel("Time")
        plt.ylabel("Normalized Value")
        plt.legend()
        plt.show()

    else:
        print("Failed to fetch data for all stocks.")

