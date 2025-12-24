from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Meta credentials (from Render environment variables)
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = "citywash123"

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
        "+91 8189822888"
    ),
    "timings": (
        "⏰ *Service Timings*\n\n"
        "🚚 Pick-up & Delivery:\n"
        "10:00 AM – 9:00 PM (All 7 days)\n\n"
        "📞 Customer Support:\n"
        "24×7 Available"
    )
}

def send_message(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
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

@app.route("/webhook", methods=["GET"])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
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
        print("Error:", e)

    return "ok", 200

if __name__ == "__main__":
    app.run()
