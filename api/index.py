# index.py
# --------------------------------------------
# Chatbot de prueba para WhatsApp Business API
# Desplegado en Vercel usando FastAPI
# --------------------------------------------

from fastapi import FastAPI, Request
import requests, os
from dotenv import load_dotenv

# Cargar variables de entorno locales (útil para pruebas locales)
load_dotenv()

# Variables necesarias (deben existir en el panel de Vercel → Environment Variables)
META_TOKEN = os.getenv("META_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Inicializar aplicación FastAPI
app = FastAPI()


# -----------------------------------------------------------
# Ruta raíz: solo para verificar que el servidor está activo
# -----------------------------------------------------------
@app.get("/")
async def home():
    return {
        "status": "ok",
        "message": "🚀 Servidor WhatsApp activo y escuchando /api/webhook"
    }


# -----------------------------------------------------------
# Verificación del webhook (GET)
# Meta enviará esta solicitud al configurar el webhook
# -----------------------------------------------------------
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


# -----------------------------------------------------------
# Recepción de mensajes (POST)
# Meta enviará aquí los mensajes entrantes
# -----------------------------------------------------------
@app.post("/api/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("📩 Webhook recibido:", data)

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])

        # Si no hay mensajes, solo se confirma la recepción
        if not messages:
            return {"status": "no_messages"}

        msg = messages[0]
        sender = msg["from"]
        text = msg["text"]["body"]

        # Procesar mensaje recibido
        reply = process_message(text)

        # Enviar respuesta al usuario por WhatsApp
        send_whatsapp_message(sender, reply)

    except Exception as e:
        print("⚠️ Error procesando mensaje:", e)

    return {"status": "ok"}


# -----------------------------------------------------------
# Función para procesar el texto entrante
# Aquí defines las respuestas automáticas
# -----------------------------------------------------------
def process_message(text: str) -> str:
    text = text.lower()

    if "hola" in text:
        return "👋 ¡Hola! Soy el asistente virtual de prueba. ¿Quieres conocer nuestro portafolio?"
    elif "portafolio" in text:
        return "🚀 Nuestro portafolio incluye desarrollo web, inteligencia artificial y automatización con chatbots."
    elif "gracias" in text:
        return "😊 ¡Con gusto! Si deseas más información, escríbeme 'portafolio'."
    else:
        return "🤔 No entendí bien, pero puedo mostrarte nuestro portafolio si lo deseas."


# -----------------------------------------------------------
# Función para enviar mensajes a través de la API de Meta
# -----------------------------------------------------------
def send_whatsapp_message(to: str, text: str):
    try:
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

    except Exception as e:
        print("❌ Error enviando mensaje:", e)
