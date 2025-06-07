# Trading Bot Example

This repository contains a small educational implementation of a EUR/USD scalping strategy.  
The core logic lives in `scalping_bot.py` and demonstrates how to calculate indicators and
produce simple trade signals.

## Strategy Overview

- Trade only during the London session (08:00–16:00 BST) and the London/New York overlap
  (13:00–16:00 BST).
- **Buy** setup:
  - Price above the 20‑SMA, 50‑SMA and 60‑EMA.
  - 20‑SMA above 50‑SMA.
  - RSI(14) above 50.
  - Bullish candlestick pattern closing above the moving averages.
- **Sell** setup: reverse the above conditions.
- Risk exactly 2% of account balance per trade using a 10–15 pip stop and 20 pip target.

The project is for educational use and does **not** execute real trades without further broker
integration.

## Trade Journal

Each trade is appended to `journal.csv` in the project directory.  The first call writes
CSV headers automatically.  You can change the journal path when creating the `ScalpingBot`:

```python
bot = ScalpingBot(balance=10000, journal_path="my_journal.csv")
```

## MetaTrader 5 Data

An optional module `mt5_feed.py` can download historical data from MetaTrader 5.  Set the
credentials in the environment variables `MT5_LOGIN`, `MT5_PASSWORD` and `MT5_SERVER` before
running:

```bash
export MT5_LOGIN=123456
export MT5_PASSWORD=secret
export MT5_SERVER=Broker-Server
```

Then call `load_mt5_data(symbol, start, end)` to obtain a DataFrame compatible with
`ScalpingBot.evaluate_signals`.

## Web Interface

A simple Flask app in `app.py` allows uploading CSV data or downloading candles from MT5 and
running the strategy.  Start it locally with:

```bash
pip install flask MetaTrader5
python app.py
```

Open <http://localhost:5000/> to view recent trades and trigger backtests.

## Hosting on Netlify

The `templates/` directory contains a very small static front‑end.  You can deploy those
static files to Netlify for free.  Note that Netlify only hosts static content—it cannot run
the Python trading logic.  Deploy by connecting your repository and using the default build
command with the publish directory set to `templates`.  A minimal `netlify.toml` is included.

