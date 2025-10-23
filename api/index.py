from fastapi import FastAPI, Request
import requests, os
from dotenv import load_dotenv

# Cargar variables locales (no afecta a Vercel, pero útil para pruebas)
load_dotenv()

META_TOKEN = os.getenv("META_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = FastAPI()

@app.get("/api/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente con Meta")
        return int(hub_challenge)
    else:
        print("❌ Token inválido o modo incorrecto")
        return {"error": "Verificación fallida"}

@app.post("/api/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("📩 Webhook recibido:", data)

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])

        if not messages:
            return {"status": "no_messages"}

        msg = messages[0]
        sender = msg["from"]
        text = msg["text"]["body"]

        reply = process_message(text)
        send_whatsapp_message(sender, reply)

    except Exception as e:
        print("⚠️ Error procesando mensaje:", e)

    return {"status": "ok"}

def process_message(text: str) -> str:
    text = text.lower()
    if "hola" in text:
        return "¡Hola! 👋 Soy el asistente virtual de prueba. ¿Quieres conocer nuestro portafolio?"
    elif "portafolio" in text:
        return "Nuestro portafolio incluye desarrollo web, IA, automatización y chatbots. 🚀"
    elif "gracias" in text:
        return "¡Con gusto! 😊 Si deseas más información, escríbeme 'portafolio'."
    else:
        return "No entendí bien 🤔, pero puedo mostrarte nuestro portafolio si lo deseas."

def send_whatsapp_message(to: str, text: str):
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📤 Meta API Response:", response.status_code, response.text)
