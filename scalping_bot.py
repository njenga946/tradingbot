"""Simple scalping bot example.

This module implements the core logic of a EUR/USD scalping strategy. It does not
connect to any broker or execute real trades. The functions are designed for
educational use and can be adapted to a real trading platform.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import List, Optional
import csv

import pandas as pd


@dataclass
class Candle:
    """Represents a single candlestick."""

    time: datetime
    open: float
    high: float
    low: float
    close: float


class ScalpingBot:
    """EUR/USD scalping strategy using SMA, EMA and RSI."""

    def __init__(self, balance: float, journal_path: str = "journal.csv") -> None:
        self.balance = balance
        self.position = None
        self.consecutive_losses = 0
        self.daily_losses = 0.0
        self.trade_history: List[dict] = []
        self.journal_path = Path(journal_path)

    @staticmethod
    def _is_london_session(ts: datetime) -> bool:
        """Return True if `ts` is within the London session."""
        london_open = time(8, 0)
        london_close = time(16, 0)
        overlap_open = time(13, 0)
        # Overlap close is same as london_close
        return london_open <= ts.time() <= london_close

    def _calculate_indicators(self, candles: pd.DataFrame) -> pd.DataFrame:
        """Return DataFrame with SMA, EMA and RSI added."""
        df = candles.copy()
        df["sma20"] = df["close"].rolling(window=20).mean()
        df["sma50"] = df["close"].rolling(window=50).mean()
        df["ema60"] = df["close"].ewm(span=60, adjust=False).mean()
        delta = df["close"].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.rolling(14).mean()
        roll_down = down.rolling(14).mean()
        rs = roll_up / roll_down
        df["rsi14"] = 100 - (100 / (1 + rs))
        return df

    def _calculate_lot_size(self, stop_pips: float) -> float:
        """Calculate lot size risking 2% of account balance."""
        risk_amount = self.balance * 0.02
        pip_value_per_lot = 10.0  # $10 per pip for 1 lot on EUR/USD
        lot_size = risk_amount / (stop_pips * pip_value_per_lot)
        return lot_size

    def _record_trade(
        self,
        direction: str,
        entry: float,
        exit_price: float,
        result: float,
        reason: str,
    ) -> None:
        record = {
            "time": datetime.now(timezone.utc).isoformat(),
            "direction": direction,
            "entry": entry,
            "exit": exit_price,
            "result": result,
            "reason": reason,
        }
        self.trade_history.append(record)
        write_header = not self.journal_path.exists()
        with self.journal_path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=record.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(record)

    def evaluate_signals(self, candles: pd.DataFrame) -> Optional[str]:
        """Return 'buy', 'sell' or None based on latest candle."""
        df = self._calculate_indicators(candles)
        last = df.iloc[-1]
        prev = df.iloc[-2]

        if not self._is_london_session(last.name.to_pydatetime()):
            return None

        bullish = last.close > last.open and prev.close < prev.open
        bearish = last.close < last.open and prev.close > prev.open

        if (
            last.close > last.sma20 > last.sma50 < float("inf")
            and last.close > last.ema60
            and last.sma20 > last.sma50
            and last.rsi14 > 50
            and bullish
        ):
            return "buy"
        if (
            last.close < last.sma20 < last.sma50 < float("inf")
            and last.close < last.ema60
            and last.sma20 < last.sma50
            and last.rsi14 < 50
            and bearish
        ):
            return "sell"
        return None

    def place_order(self, direction: str, price: float, stop_pips: float = 15.0) -> None:
        """Mock placing an order and recording it."""
        lot_size = self._calculate_lot_size(stop_pips)
        # In a real system, an API call would be made here.
        print(f"Placing {direction} order: lot {lot_size:.2f} at {price}")
        # Record trade for demonstration
        self._record_trade(direction, price, price, 0.0, "entry")

    # Additional methods for managing open positions would go here.


def load_csv(path: str) -> pd.DataFrame:
    """Utility to load candle data from CSV."""
    df = pd.read_csv(path, parse_dates=["time"])
    df.set_index("time", inplace=True)
    return df


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run scalping bot on CSV data")
    parser.add_argument("csv", help="CSV file with columns: time,open,high,low,close")
    parser.add_argument("--journal", default="journal.csv", help="Path to trade journal CSV")
    args = parser.parse_args()

    data = load_csv(args.csv)
    bot = ScalpingBot(balance=10000.0, journal_path=args.journal)

    for i in range(60, len(data)):
        window = data.iloc[i - 60 : i + 1]
        signal = bot.evaluate_signals(window)
        if signal:
            price = window.iloc[-1].close
            bot.place_order(signal, price)

