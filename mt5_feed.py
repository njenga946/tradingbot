import os
from datetime import datetime
import pandas as pd

try:
    import MetaTrader5 as mt5
except ImportError:  # pragma: no cover - optional dependency
    mt5 = None


def _ensure_initialized() -> None:
    if mt5 is None:
        raise RuntimeError("MetaTrader5 package is not installed")
    if mt5.terminal_info() is None:
        login = int(os.getenv("MT5_LOGIN", 0))
        password = os.getenv("MT5_PASSWORD")
        server = os.getenv("MT5_SERVER")
        if not mt5.initialize(login=login, password=password, server=server):
            raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")


def load_mt5_data(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    """Load historical data from MetaTrader 5."""
    _ensure_initialized()
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, start, end)
    mt5.shutdown()
    if rates is None:
        raise RuntimeError(f"Failed to copy rates: {mt5.last_error()}")
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close'}, inplace=True)
    df.set_index('time', inplace=True)
    return df[['open', 'high', 'low', 'close']]
