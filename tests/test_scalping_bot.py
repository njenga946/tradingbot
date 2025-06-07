import pandas as pd
from datetime import datetime, timezone

from scalping_bot import ScalpingBot

def test_lot_size():
    bot = ScalpingBot(balance=10000)
    size = bot._calculate_lot_size(10)
    assert round(size, 4) == 2.0


def test_is_london_session():
    bot = ScalpingBot(balance=1000)
    dt_in = datetime(2020, 1, 1, 9, 0, tzinfo=timezone.utc)
    assert bot._is_london_session(dt_in)
    dt_out = datetime(2020, 1, 1, 7, 59, tzinfo=timezone.utc)
    assert not bot._is_london_session(dt_out)
    dt_close = datetime(2020, 1, 1, 16, 0, tzinfo=timezone.utc)
    assert bot._is_london_session(dt_close)
    dt_after = datetime(2020, 1, 1, 16, 1, tzinfo=timezone.utc)
    assert not bot._is_london_session(dt_after)


def test_calculate_indicators():
    data = [
        {
            "time": datetime(2020, 1, 1, 8, 0, tzinfo=timezone.utc) + pd.Timedelta(minutes=5 * i),
            "open": 1 + i * 0.001,
            "high": 1 + i * 0.001 + 0.0005,
            "low": 1 + i * 0.001 - 0.0005,
            "close": 1 + i * 0.001 + 0.0002,
        }
        for i in range(60)
    ]
    df = pd.DataFrame(data).set_index("time")
    bot = ScalpingBot(balance=1000)
    out = bot._calculate_indicators(df)
    last = out.iloc[-1]
    assert last["sma20"] > 0
    assert last["ema60"] > 0
    assert last["rsi14"] >= 0


def test_evaluate_signals_buy():
    # create upward trending data to trigger buy signal
    data = []
    for i in range(60):
        ts = datetime(2020, 1, 1, 8, 0, tzinfo=timezone.utc) + pd.Timedelta(minutes=5 * i)
        if i == 59:
            open_price = 1 + 0.01 * i - 0.002
            close = 1 + 0.01 * i
        elif i == 58:
            open_price = 1 + 0.01 * i
            close = open_price - 0.002
        else:
            open_price = 1 + 0.01 * i - 0.0002
            close = 1 + 0.01 * i
        data.append({
            "time": ts,
            "open": open_price,
            "high": max(open_price, close),
            "low": min(open_price, close),
            "close": close,
        })
    df = pd.DataFrame(data).set_index("time")
    bot = ScalpingBot(balance=1000)
    signal = bot.evaluate_signals(df)
    assert signal == "buy"
