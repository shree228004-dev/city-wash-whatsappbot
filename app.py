from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ==================================================
# ENVIRONMENT VARIABLES (SET IN RENDER)
# ==================================================
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

# ==================================================
# HOME ROUTE (OPTIONAL)
# ==================================================
@app.route("/", methods=["GET"])
def home():
    return "WhatsApp webhook is running ✅", 200

# ==================================================
# WEBHOOK VERIFICATION (META CALLS THIS)
# ==================================================
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("MODE:", mode)
    print("TOKEN RECEIVED:", token)
    print("TOKEN EXPECTED:", VERIFY_TOKEN)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403

# ==================================================
# RECEIVE WHATSAPP MESSAGES
# ==================================================
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("WEBHOOK DATA:", data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "ok", 200

        message = value["messages"][0]

        if "text" not in message:
            return "ok", 200

        from_number = message["from"]
        user_text = message["text"]["body"].lower()

        if "hi" in user_text or "hello" in user_text:
            reply_text = (
                "👋 Welcome to *City Wash Laundry Services*!\n\n"
                "Reply with:\n"
                "📍 Location\n"
                "☎ Contact\n"
                "⏰ Timings"
            )
        elif "location" in user_text:
            reply_text = (
                "📍 *City Wash Laundry Services*\n"
                "No. 9, Thendral Nagar,\n"
                "Sathuvachari, Vellore – 632009\n"
                "https://maps.google.com/?q=City+Wash+Laundry+Services+Vellore"
            )
        elif "contact" in user_text:
            reply_text = (
                "☎ *Contact Us*\n"
                "+91 81898 00888\n"
                "+91 81898 22888"
            )
        elif "time" in user_text or "timing" in user_text:
            reply_text = (
                "⏰ *Service Timings*\n\n"
                "10:00 AM – 9:00 PM\n"
                "All 7 days"
            )
        else:
            reply_text = "❓ Please reply with *Location*, *Contact*, or *Timings*."

        send_whatsapp_message(from_number, reply_text)

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200

# ==================================================
# SEND WHATSAPP MESSAGE
# ==================================================
def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("SEND STATUS:", response.status_code)
    print("SEND RESPONSE:", response.text)

# ==================================================
# APP START (RENDER COMPATIBLE)
# ==================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

