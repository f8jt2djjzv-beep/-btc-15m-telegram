import os
import requests
import pandas as pd

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def obtener_datos():
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": "BTCUSDT",
        "interval": "15m",
        "limit": 100
    }

    respuesta = requests.get(
        url,
        params=params,
        timeout=10
    )

    respuesta.raise_for_status()

    datos = respuesta.json()

    df = pd.DataFrame(
        datos,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "buy_volume",
            "buy_quote_volume",
            "ignore"
        ]
    )

    df["close"] = df["close"].astype(float)

    return df


def calcular_rsi(series, periodo=14):
    delta = series.diff()

    ganancias = delta.clip(lower=0)
    perdidas = -delta.clip(upper=0)

    promedio_ganancia = ganancias.rolling(periodo).mean()
    promedio_perdida = perdidas.rolling(periodo).mean()

    rs = promedio_ganancia / promedio_perdida

    return 100 - (100 / (1 + rs))


def analizar():
    df = obtener_datos()

    df["ema9"] = df["close"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["ema21"] = df["close"].ewm(
        span=21,
        adjust=False
    ).mean()

    df["rsi"] = calcular_rsi(
        df["close"]
    )

    ultimo = df.iloc[-1]

    precio = ultimo["close"]
    ema9 = ultimo["ema9"]
    ema21 = ultimo["ema21"]
    rsi = ultimo["rsi"]

    if ema9 > ema21 and rsi > 50:
        señal = "🟢 POSIBLE SUBIDA"

    elif ema9 < ema21 and rsi < 50:
        señal = "🔴 POSIBLE BAJADA"

    else:
        señal = "⚪ SEÑAL DÉBIL / ESPERAR"

    mensaje = f"""
₿ BTC/USDT — 15 MIN

💰 Precio: ${precio:,.2f}

📊 EMA 9: {ema9:,.2f}
📊 EMA 21: {ema21:,.2f}
📈 RSI 14: {rsi:.2f}

🔔 Señal:
{señal}

⚠️ Señal técnica, no garantía de movimiento.
"""

    return mensaje


mensaje = analizar()

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

respuesta = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": mensaje
    },
    timeout=10
)

print("Respuesta de Telegram:")
print(respuesta.text)

respuesta.raise_for_status()
