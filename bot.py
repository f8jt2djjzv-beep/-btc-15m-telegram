import os
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": "🤖 ¡Prueba exitosa! Tu bot de Telegram está conectado."
    },
    timeout=10
)

print("Respuesta de Telegram:")
print(response.text)

response.raise_for_status()
