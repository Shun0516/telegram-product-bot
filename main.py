import telebot
import openai
from flask import Flask, request
import os

# --- CONFIG ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENROUTER_API_KEY

# --- FLASK APP ---
app = Flask(__name__)

# --- TELEGRAM WEBHOOK ENDPOINT ---
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def receive_update():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# --- TELEBOT HANDLERS ---
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.reply_to(message, "👋 Hi seller! Send me your product info and I’ll write a catchy Taglish description for you. 🛍️")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    prompt = f"You're an expert online seller. Write a short, catchy, Taglish product description based on this info: {message.text}. Include emojis. Keep it conversational and fun."

    try:
        response = openai.ChatCompletion.create(
            model="openrouter/meta-llama-3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            api_base="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
        reply = response.choices[0].message.content.strip()
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# --- RUN FLASK ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
