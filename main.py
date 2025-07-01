import os
import telebot
import requests

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = "meta-llama/llama-3-70b-instruct"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- HANDLERS ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "👋 Hi seller! Send me your product info and I’ll write a catchy Taglish description for you. 🛍️")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_input = message.text
    prompt = f"You're an expert online seller. Write a short, catchy, Taglish product description based on this info: {user_input}. Include emojis. Keep it conversational and fun."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://yourdomain.com",  # Optional but recommended
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        result = response.json()

        if "choices" in result:
            reply = result["choices"][0]["message"]["content"]
            bot.reply_to(message, reply.strip())
        else:
            error_msg = result.get("error", {}).get("message", "Unknown error.")
            bot.reply_to(message, f"❌ Error: {error_msg}")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# --- START BOT ---
print("🤖 Bot is running...")
bot.infinity_polling()