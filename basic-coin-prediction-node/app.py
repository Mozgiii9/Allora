from flask import Flask, jsonify
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from config import data_base_path
import random
import requests
import retrying
import threading
import time

app = Flask(__name__)

forecast_price = {}

binance_data_path = os.path.join(data_base_path, "binance/futures-klines")
MAX_DATA_SIZE = 100
INITIAL_FETCH_SIZE = 100

@retrying.retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def fetch_prices(symbol, interval="1m", limit=100, start_time=None, end_time=None):
    try:
        base_url = "https://fapi.binance.com"
        endpoint = f"/fapi/v1/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time

        url = base_url + endpoint
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f'Не удалось получить цены для {symbol} из Binance API: {str(e)}')
        raise e

def download_data(token):
    symbols = f"{token.upper()}USDT"
    interval = "5m"
    current_datetime = datetime.now()
    download_path = os.path.join(binance_data_path, token.lower())

    file_path = os.path.join(download_path, f"{token.lower()}_5m_data.csv")

    if os.path.exists(file_path):
        start_time = int((current_datetime - timedelta(minutes=500)).timestamp() * 1000)
        end_time = int(current_datetime.timestamp() * 1000)
        new_data = fetch_prices(symbols, interval, 100, start_time, end_time)
    else:
        start_time = int((current_datetime - timedelta(minutes=INITIAL_FETCH_SIZE * 5)).timestamp() * 1000)
        end_time = int(current_datetime.timestamp() * 1000)
        new_data = fetch_prices(symbols, interval, INITIAL_FETCH_SIZE, start_time, end_time)

    new_df = pd.DataFrame(new_data, columns=[
        "start_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignore"
    ])

    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        combined_df = pd.concat([old_df, new_df])
        combined_df = combined_df.drop_duplicates(subset=['start_time'], keep='last')
    else:
        combined_df = new_df

    if len(combined_df) > MAX_DATA_SIZE:
        combined_df = combined_df.iloc[-MAX_DATA_SIZE:]

    if not os.path.exists(download_path):
        os.makedirs(download_path)
    combined_df.to_csv(file_path, index=False)
    print(f"Обновленные данные для {token} сохранены в {file_path}. Всего строк: {len(combined_df)}")

def format_data(token):
    path = os.path.join(binance_data_path, token.lower())
    file_path = os.path.join(path, f"{token.lower()}_5m_data.csv")

    if not os.path.exists(file_path):
        print(f"Файл данных для {token} не найден")
        return

    df = pd.read_csv(file_path)

    columns_to_use = [
        "start_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume"
    ]

    if set(columns_to_use).issubset(df.columns):
        df = df[columns_to_use]
        df.columns = [
            "start_time", "open", "high", "low", "close", "volume",
            "end_time", "quote_asset_volume", "n_trades",
            "taker_volume", "taker_volume_usd"
        ]
        df.index = pd.to_datetime(df["start_time"], unit='ms')
        df.index.name = "date"

        output_path = os.path.join(data_base_path, f"{token.lower()}_price_data.csv")
        df.sort_index().to_csv(output_path)
        print(f"Форматированные данные сохранены в {output_path}")
    else:
        print(f"Необходимые колонки отсутствуют в {file_path}. Пропускаем этот файл.")

def train_model(token):
    time_start = datetime.now()

    price_data = pd.read_csv(os.path.join(data_base_path, f"{token.lower()}_price_data.csv"))
    df = pd.DataFrame()

    price_data["date"] = pd.to_datetime(price_data["date"])
    price_data.set_index("date", inplace=True)

    df = price_data.resample('20T').mean()

    df = df.dropna()
    X = np.array(range(len(df))).reshape(-1, 1)
    y = df['close'].values

    model = LinearRegression()
    model.fit(X, y)

    next_time_index = np.array([[len(df)]])
    predicted_price = model.predict(next_time_index)[0]

    fluctuation_range = 0.001 * predicted_price
    min_price = predicted_price - fluctuation_range
    max_price = predicted_price + fluctuation_range

    price_predict = random.uniform(min_price, max_price)

    forecast_price[token] = price_predict

    print(f"Прогноз для {token}: {forecast_price[token]}")

    time_end = datetime.now()
    print(f"Затраченное время на прогноз: {time_end - time_start}")

@app.route('/inference/<token>', methods=['GET'])
def inference(token):
    if token in forecast_price:
        return jsonify({token: forecast_price[token]})
    else:
        return jsonify({"error": f"No forecast found for {token}"}), 404

def update_data():
    tokens = ["ETH", "BNB", "ARB"]
    for token in tokens:
        print(f"Загрузка данных и расчет прогноза для {token}")
        download_data(token)
        format_data(token)
        train_model(token)

# Функция для периодического обновления данных
def periodic_update():
    while True:
        print("Обновление данных и прогнозов")
        update_data()
        time.sleep(15)  # Период обновления каждые 15 секунд

# Запуск периодического обновления данных в отдельном потоке
threading.Thread(target=periodic_update, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)

