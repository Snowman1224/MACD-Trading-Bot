# region imports
from AlgorithmImports import *
from macd_atr_strategy import MACDATRStrategy 
# endregion

class FatYellowGreenDuck(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)
        
        # List of symbols to trade
        self.symbols = ["TSLA"]

        self.strategies = {}  # Dictionary to hold strategies for each symbol
        self.stop_profit_targets = {}  # Profit target for each symbol
        self.stop_loss_prices = {}  # Stop loss for each symbol

        # Requesting minute resolution data for each symbol and setting up strategies
        for symbol in self.symbols:
            equity = self.AddEquity(symbol, Resolution.Minute).Symbol
            self.strategies[equity] = MACDATRStrategy(decrease_percentage=0., sd_multiplier=0)  # Create a new strategy instance for each symbol
            
            # Create a 30-minute consolidator for each stock
            consolidator = TradeBarConsolidator(timedelta(minutes=30))
            consolidator.DataConsolidated += lambda sender, bar, sym=equity: self.OnDataConsolidated(sender, bar, sym)
            self.SubscriptionManager.AddConsolidator(equity, consolidator)

    def OnData(self, data):
        for symbol in self.symbols:
            if data.Bars.ContainsKey(symbol):
                self.SellStock(symbol, data[symbol].Close)

    def OnDataConsolidated(self, sender, bar, symbol):
        signal = self.strategies[symbol].update(bar.Close, bar.High, bar.Low)

        # Execute buy signal
        if signal and signal["signal"] == "Buy":
            self.ExecuteBuy(symbol, signal)

    def ExecuteBuy(self, symbol, signal):
        num_held_stocks = sum(1 for holding in self.Portfolio.Values if holding.Invested)
        stock = str(symbol)
        if num_held_stocks < 2:
            allocation = 0.5 if num_held_stocks == 0 else self.Portfolio.Cash / self.Portfolio.TotalPortfolioValue
            self.SetHoldings(stock, allocation)
            
            # Store stop profit target and stop loss price
            self.stop_profit_targets[stock] = signal['stop_profit_target']
            self.stop_loss_prices[stock] = signal['stop_loss_price']
            
            # Debug print statements
            self.Debug(f"Executed Buy on {stock} at {self.Portfolio[symbol].Price:.2f}, "
                    f"with target price {self.stop_profit_targets[stock]:.2f} "
                    f"and stop loss {self.stop_loss_prices[stock]:.2f}")

    def SellStock(self, symbol, current_price):
        stock = str(symbol)
        if self.Portfolio[stock].Invested:
            # Accessing stop profit target and stop loss price with the correct key
            stop_profit_target = self.stop_profit_targets.get(stock, None)
            stop_loss_price = self.stop_loss_prices.get(stock, None)

            # Check for stop profit or stop loss conditions
            if stop_profit_target and current_price >= stop_profit_target:
                self.Liquidate(stock)
                self.Debug(f"Sold {stock} at {current_price:.2f}, reached profit target of {stop_profit_target:.2f}.")
            elif stop_loss_price and current_price <= stop_loss_price:
                self.Liquidate(symbol)
                self.Debug(f"Sold {stock} at {current_price:.2f}, hit stop loss of {stop_loss_price:.2f}.")

