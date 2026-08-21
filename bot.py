import os
import requests
import time
from datetime import datetime, timezone

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

def get_btc_price():
    data = requests.get(
        "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
        timeout=10
    ).json()
    return float(data["price"])

def analyze():
    prices = []

    for _ in range(5):
        prices.append(get_btc_price())
        time.sleep(10)

    change = (prices[-1] - prices[0]) / prices[0] * 100

    if change > 0.02:
        signal = "🟢 BTC UP"
    elif change < -0.02:
        signal = "🔴 BTC DOWN"
    else:
        signal = "⚪ SIN SEÑAL"

    return (
        f"{signal}\n\n"
        f"BTC: ${prices[-1]:,.2f}\n"
        f"Movimiento: {change:+.3f}%\n"
        f"Hora: {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC"
    )

while True:
    try:
        send_message(analyze())
    except Exception as e:
        print("Error:", e)

    time.sleep(900)
