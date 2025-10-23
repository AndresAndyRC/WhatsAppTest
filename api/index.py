# --------------------------------------------
# Chatbot de prueba para WhatsApp Business API
# Desplegado en Vercel usando FastAPI
# Autor: AndresAndyRC
# --------------------------------------------

from fastapi import FastAPI, Request
from fastapi.responses import Response
import requests, os
from dotenv import load_dotenv

# -----------------------------------------------------------
# Cargar variables de entorno (para entorno local o Vercel)
# -----------------------------------------------------------
load_dotenv()

META_TOKEN = os.getenv("META_TOKEN")   # Token de acceso de la API de Meta
PHONE_ID = os.getenv("PHONE_ID")       # ID del número de WhatsApp Business
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # Token para verificar el webhook

# -----------------------------------------------------------
# Inicializar aplicación FastAPI
# -----------------------------------------------------------
app = FastAPI()


# -----------------------------------------------------------
# Ruta raíz: para confirmar que el servidor está activo
# -----------------------------------------------------------
@app.get("/")
async def home():
    return {
        "status": "ok",
        "message": "🚀 Servidor WhatsApp activo y escuchando /api/webhook"
    }


# -----------------------------------------------------------
# ✅ Verificación del Webhook (GET)
# Meta enviará esta solicitud al configurar el webhook
# -----------------------------------------------------------
@app.get("/api/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Validar token
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado correctamente con Meta")
        # Meta espera una respuesta tipo texto plano, no JSON
        return Response(content=challenge, media_type="text/plain")
    else:
        print("❌ Token inválido o modo incorrecto")
        return {"error": "Verificación fallida"}


# -----------------------------------------------------------
# 📩 Recepción de mensajes (POST)
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

        # Si no hay mensajes (por ejemplo, actualizaciones de estado)
        if not messages:
            return {"status": "no_messages"}

        msg = messages[0]
        sender = msg["from"]  # Número del usuario
        text = msg["text"]["body"]  # Texto del mensaje recibido

        # Procesar mensaje recibido
        reply = process_message(text)

        # Enviar respuesta por WhatsApp
        send_whatsapp_message(sender, reply)

    except Exception as e:
        print("⚠️ Error procesando mensaje:", e)

    return {"status": "ok"}


# -----------------------------------------------------------
# 🧠 Procesamiento del mensaje (lógica del bot)
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
# ✉️ Enviar mensaje a través de la API de Meta
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