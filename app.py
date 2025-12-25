from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================== CONFIG ==================
VERIFY_TOKEN = "citywash123"
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# ================== HOME ==================
@app.route("/", methods=["GET"])
def home():
    return "City Wash WhatsApp Bot is running ✅", 200

# ================== WEBHOOK VERIFY ==================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403

# ================== SEND MESSAGE ==================
def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
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
    requests.post(url, headers=headers, json=payload)

# ================== WEBHOOK RECEIVE ==================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("INCOMING:", data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "ok", 200

        message = value["messages"][0]
        sender = message["from"]
        text = message["text"]["body"].lower()

        if "hi" in text or "hello" in text:
            reply = (
                "👋 Welcome to *City Wash Laundry Services*!\n\n"
                "Reply with:\n"
                "📍 Location\n"
                "☎ Contact\n"
                "⏰ Timings"
            )
        elif "location" in text:
            reply = (
                "📍 *City Wash Laundry Services*\n"
                "No. 9, Thendral Nagar,\n"
                "Sathuvachari, Vellore – 632009\n"
                "https://maps.google.com/?q=City+Wash+Laundry+Services+Vellore"
            )
        elif "contact" in text:
            reply = "☎ +91 81898 00888\n☎ +91 81898 22888"
        elif "time" in text or "timing" in text:
            reply = "⏰ 10:00 AM – 9:00 PM (All 7 days)"
        else:
            reply = "❓ Please reply with *Location*, *Contact*, or *Timings*."

        send_message(sender, reply)

    except Exception as e:
        print("ERROR:", e)

    return "ok", 200

# ================== RUN ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
