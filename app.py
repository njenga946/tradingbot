from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from scalping_bot import ScalpingBot
from mt5_feed import load_mt5_data

app = Flask(__name__)
bot = ScalpingBot(balance=10000.0)

@app.route('/')
def index():
    return render_template('index.html', trades=bot.trade_history)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        df = pd.read_csv(file, parse_dates=['time'])
        df.set_index('time', inplace=True)
        for i in range(60, len(df)):
            window = df.iloc[i-60:i+1]
            signal = bot.evaluate_signals(window)
            if signal:
                price = window.iloc[-1].close
                bot.place_order(signal, price)
    return redirect(url_for('index'))

@app.route('/mt5', methods=['POST'])
def run_mt5():
    symbol = request.form.get('symbol', 'EURUSD')
    start = pd.to_datetime(request.form['start'])
    end = pd.to_datetime(request.form['end'])
    df = load_mt5_data(symbol, start, end)
    for i in range(60, len(df)):
        window = df.iloc[i-60:i+1]
        signal = bot.evaluate_signals(window)
        if signal:
            price = window.iloc[-1].close
            bot.place_order(signal, price)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
