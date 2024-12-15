import numpy as np
import talib


class MACDATRStrategy:
    def __init__(self, fast_length=13, slow_length=34, signal_length=9,
                 decrease_percentage=0.2, atr_length=13, atr_multiplier=1.5,
                 sd_length=13, sd_multiplier=2, atr_min_multiplier=0.8, atr_max_multiplier=3, rsi_length=14, rsi_buy_threshold=30, rsi_sell_threshold=70):
        # Initialize parameters
        self.fast_length = fast_length
        self.slow_length = slow_length
        self.signal_length = signal_length
        self.decrease_percentage = decrease_percentage
        self.atr_length = atr_length
        self.atr_multiplier = atr_multiplier  # Base ATR multiplier
        self.sd_length = sd_length
        self.sd_multiplier = sd_multiplier
        self.atr_min_multiplier = atr_min_multiplier  # Minimum ATR multiplier
        self.atr_max_multiplier = atr_max_multiplier  # Maximum ATR multiplier

        # RSI parameters
        self.rsi_length = rsi_length
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold

        # Internal state
        self.peak_values = []
        self.close_prices = []
        self.high = []
        self.low = []
        self.is_in_position = False
        self.buy_price = None
        self.atr = None
        self.stop_loss_price = None
        self.stop_profit_target = None

    def calculate_macd(self):
        macd, macd_signal, macd_hist = talib.MACD(np.array(self.close_prices),
                                                  fastperiod=self.fast_length,
                                                  slowperiod=self.slow_length,
                                                  signalperiod=self.signal_length)
        return macd, macd_signal, macd_hist

    def calculate_atr(self, dynamic_multiplier):
        # Apply dynamic ATR multiplier to adjust stop-loss and profit levels
        return talib.ATR(np.array(self.high),
                         np.array(self.low),
                         np.array(self.close_prices),
                         timeperiod=self.atr_length) * dynamic_multiplier

    def calculate_rsi(self):
        # Calculate RSI using close prices
        return talib.RSI(np.array(self.close_prices), timeperiod=self.rsi_length)

    def calculate_sd(self):
        return talib.STDDEV(np.array(self.close_prices), timeperiod=self.sd_length)

    def calculate_dynamic_atr_multiplier(self):
        # Calculate volatility using standard deviation of recent close prices
        volatility = self.calculate_sd()[-1]
        # Adjust the ATR multiplier dynamically based on volatility
        dynamic_multiplier = self.atr_multiplier * (1 + volatility)
        # Clamp the multiplier between the min and max limits
        return max(self.atr_min_multiplier, min(self.atr_max_multiplier, dynamic_multiplier))

    def update(self, close, high, low):
        # Append the current price to the price history
        self.close_prices.append(close)
        self.high.append(high)
        self.low.append(low)

        # Calculate MACD
        macd, macd_signal, macd_hist = self.calculate_macd()
        rsi = self.calculate_rsi()

        if len(macd_hist) < self.slow_length + self.signal_length + 1:
            return None  # Not enough data to make a decision

        current_macd_hist = macd_hist[-1]
        previous_macd_hist = macd_hist[-2]
        two_bars_ago_macd_hist = macd_hist[-3]
        current_rsi = rsi[-1]

        # Check for peak conditions
        if (previous_macd_hist <= two_bars_ago_macd_hist and
                current_macd_hist > previous_macd_hist and
                two_bars_ago_macd_hist < 0 and
                previous_macd_hist < 0 and
                current_macd_hist < 0):
            self.peak_values.append(previous_macd_hist)

        # Generate sell signal
        if self.is_in_position:
            if low <= self.stop_loss_price:
                self.is_in_position = False
                return {
                    "signal": "Sell",
                    "sell_price": self.stop_loss_price,
                    "profit/loss": self.buy_price - self.stop_loss_price
                }
            elif high >= self.stop_profit_target:
                self.is_in_position = False
                return {
                    "signal": "Sell",
                    "sell_price": self.stop_profit_target,
                    "profit/loss": self.stop_profit_target - self.buy_price
                }
            # elif current_rsi >= self.rsi_sell_threshold:  # RSI sell confirmation
            #     self.is_in_position = False
            #     return {
            #         "signal": "Sell",
            #         "sell_price": close,
            #         "profit": close - self.buy_price
            #     }
            else:
                return None

        if len(self.peak_values) >= 2:
            peak_current = self.peak_values[-1]
            peak_previous = self.peak_values[-2]
            sd_current = self.calculate_sd()[-1]

            condition_decrease = (peak_previous * (1 - self.decrease_percentage) < peak_current)

            # Generate buy signal
            if (condition_decrease and
                    (self.close_prices[-2] - sd_current * self.sd_multiplier > self.close_prices[-1])
                    and not self.is_in_position
                    and current_rsi <= self.rsi_buy_threshold
                    ):
                self.buy_price = close
                dynamic_atr_multiplier = self.calculate_dynamic_atr_multiplier()  # Adjusted multiplier
                atr = self.calculate_atr(dynamic_atr_multiplier)
                self.atr = atr[-1]
                self.stop_profit_target = self.buy_price + 1.5 * (self.buy_price - (low - self.atr))
                self.stop_loss_price = low - self.atr
                self.is_in_position = True
                return {
                    "signal": "Buy",
                    "buy_price": self.buy_price,
                    "stop_profit_target": self.stop_profit_target,
                    "stop_loss_price": self.stop_loss_price
                }

        return None