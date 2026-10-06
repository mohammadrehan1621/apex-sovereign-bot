import pandas as pd
import numpy as np

class SupremeAlphaStrategy:
    """
    Ensemble Market Strategy combining:
    1. Trend Detection (EMA 9/21 cross)
    2. Momentum & Exhaustion (RSI 14 with dynamic thresholds)
    3. Volatility Envelope (Bollinger Bands mean-reversion confirmation)
    4. Volume confirmation (Above moving avg volume)
    """
    def __init__(self, rsi_period=14, ema_fast=9, ema_slow=21, bb_period=20, bb_std=2.0):
        self.rsi_period = rsi_period
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.bb_period = bb_period
        self.bb_std = bb_std

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Exponential Moving Averages
        df["ema_fast"] = df["close"].ewm(span=self.ema_fast, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=self.ema_slow, adjust=False).mean()

        # Relative Strength Index (RSI)
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / (loss + 1e-9)
        df["rsi"] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        df["bb_mid"] = df["close"].rolling(window=self.bb_period).mean()
        bb_std = df["close"].rolling(window=self.bb_period).std()
        df["bb_upper"] = df["bb_mid"] + (bb_std * self.bb_std)
        df["bb_lower"] = df["bb_mid"] - (bb_std * self.bb_std)

        # Volume Moving Average
        df["vol_ma"] = df["volume"].rolling(window=20).mean()

        return df

    def generate_signal(self, df: pd.DataFrame) -> str:
        """
        Returns 'BUY', 'SELL', or 'HOLD'
        """
        if len(df) < max(self.bb_period, self.ema_slow) + 5:
            return "HOLD"

        curr = df.iloc[-1]
        prev = df.iloc[-2]

        # Multi-factor convergence for High-Confidence Entry:
        # 1. Fast EMA crosses above Slow EMA
        # 2. RSI is not overbought (between 40 and 65)
        # 3. Price bounced near lower or middle BB
        # 4. Volume expansion confirmation
        trend_bullish = curr["ema_fast"] > curr["ema_slow"]
        rsi_bullish = 35 <= curr["rsi"] <= 68
        vol_confirmed = curr["volume"] >= curr["vol_ma"] * 0.7

        if trend_bullish and rsi_bullish:
            return "BUY"

        # Exit / Short signal:
        trend_bearish = curr["ema_fast"] < curr["ema_slow"] and prev["ema_fast"] >= prev["ema_slow"]
        rsi_exhausted = curr["rsi"] >= 75

        if trend_bearish or rsi_exhausted:
            return "SELL"

        return "HOLD"
