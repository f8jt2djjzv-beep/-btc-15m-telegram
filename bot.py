import os
import requests
import pandas as pd

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def obtener_datos():
    url = "https://api.exchange.coinbase.com/products/BTC-USD/candles"

    respuesta = requests.get(
        url,
        params={"granularity": 900},
        timeout=10,
        headers={"User-Agent": "BTC-15M-Telegram-Bot"}
    )

    respuesta.raise_for_status()

    datos = respuesta.json()

    df = pd.DataFrame(
        datos,
        columns=[
            "time",
            "low",
            "high",
            "open",
            "close",
            "volume"
        ]
    )

    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    df = df.sort_values("time").reset_index(drop=True)

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

    df["rsi"] = calcular_rsi(df["close"])

    df["momentum"] = df["close"].pct_change(4) * 100

    ultimo = df.iloc[-1]

    precio = ultimo["close"]
    ema9 = ultimo["ema9"]
    ema21 = ultimo["ema21"]
    rsi = ultimo["rsi"]
    momentum = ultimo["momentum"]

    puntuacion = 50

    # EMA
    if ema9 > ema21:
        puntuacion += 15
    else:
        puntuacion -= 15

    # RSI
    if rsi > 55:
        puntuacion += 15
    elif rsi > 50:
        puntuacion += 7
    elif rsi < 45:
        puntuacion -= 15
    elif rsi < 50:
        puntuacion -= 7

    # Momentum
    if momentum > 0.10:
        puntuacion += 10
    elif momentum > 0:
        puntuacion += 5
    elif momentum < -0.10:
        puntuacion -= 10
    elif momentum < 0:
        puntuacion -= 5

    puntuacion = max(10, min(90, puntuacion))

    subida = puntuacion
    bajada = 100 - subida

    if subida >= 60:
        señal = "🟢 POSIBLE SUBIDA"
    elif bajada >= 60:
        señal = "🔴 POSIBLE BAJADA"
    else:
        señal = "⚪ MERCADO INCIERTO"

    mensaje = f"""
₿ BTC/USD — 15 MIN

💰 Precio: ${precio:,.2f}

🟢 Subida estimada: {subida:.0f}%
🔴 Bajada estimada: {bajada:.0f}%

📊 EMA 9: {ema9:,.2f}
📊 EMA 21: {ema21:,.2f}
📈 RSI 14: {rsi:.2f}
⚡ Momentum: {momentum:.3f}%

🔔 Señal:
{señal}

⚠️ Porcentajes = puntuación técnica del bot,
no una probabilidad garantizada.
"""

    return mensaje


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    respuesta = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": mensaje
        },
        timeout=10
    )

    print(respuesta.text)

    respuesta.raise_for_status()


mensaje = analizar()

print(mensaje)

enviar_telegram(mensaje)
