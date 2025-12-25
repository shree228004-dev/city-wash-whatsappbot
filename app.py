from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ================== ENVIRONMENT VARIABLES ==================
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

# ================== BOT RESPONSES ==================
CITY_WASH = {
    "welcome": (
        "👋 Welcome to *City Wash Laundry Services*!\n\n"
        "We provide fast, affordable & eco-friendly laundry services 🧺✨\n\n"
        "Reply with:\n"
        "📍 Location\n"
        "☎ Contact\n"
        "⏰ Timings"
    ),
    "location": (
        "📍 *City Wash Laundry Services*\n"
        "No. 9, Thendral Nagar,\n"
        "Sathuvachari, Vellore – 632009\n\n"
        "🔗 https://maps.google.com/?q=City+Wash+Laundry+Services+Vellore"
    ),
    "contact": (
        "☎ *Contact Us*\n"
        "+91 81898 00888\n"
        "+91 81898 22888"
    ),
    "timings": (
        "⏰ *Service Timings*\n\n"
        "🚚 Pick-up & Delivery:\n"
        "10:00 AM – 9:00 PM (All 7 days)\n\n"
        "📞 Customer Support:\n"
        "24×7 Available"
    )
}

# ================== HOME ROUTE ==================
@app.route("/", methods=["GET"])
def home():
    return "City Wash WhatsApp Bot is running ✅", 200


# ================== SEND WHATSAPP MESSAGE ==================
def send_message(to, text):
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
    print("SEND MESSAGE STATUS:", response.status_code)
    print("SEND MESSAGE RESPONSE:", response.text)


# ================== WEBHOOK VERIFICATION (META) ==================
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("VERIFY TOKEN RECEIVED:", token)
    print("VERIFY TOKEN EXPECTED:", VERIFY_TOKEN)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403


# ================== RECEIVE WHATSAPP MESSAGES ==================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("FULL WEBHOOK DATA:", data)

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        # Ignore non-message events
        if "messages" not in value:
            return "ok", 200

        message = value["messages"][0]

        # Ignore non-text messages
        if "text" not in message:
            return "ok", 200

        user_text = message["text"]["body"].lower()
        user_number = message["from"]

        if "hi" in user_text or "hello" in user_text:
            reply = CITY_WASH["welcome"]
        elif "location" in user_text:
            reply = CITY_WASH["location"]
        elif "contact" in user_text or "phone" in user_text:
            reply = CITY_WASH["contact"]
        elif "time" in user_text or "timing" in user_text:
            reply = CITY_WASH["timings"]
        else:
            reply = "❓ Please reply with *Location*, *Contact*, or *Timings*."

        send_message(user_number, reply)

    except Exception as e:
        print("WEBHOOK ERROR:", e)

    return "ok", 200


# ================== APP START (RENDER) ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
