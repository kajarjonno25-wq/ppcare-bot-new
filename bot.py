from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import requests
import os
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8683913109:AAGqeL4FleykAuOIoqeoSFQ77H4pryBewG4"
SUPABASE_URL = "https://kzvnwugoyqbyxslxzzul.supabase.co"
SUPABASE_KEY = "sb_publishable_OlsWkOtI5JjJ0UBZLqsP8Q_T4kS3xsG"

# Webhook URL হবে পরে Render URL দেওয়ার পর
WEBAPP_URL = "https://YOUR_VERCEL_URL.vercel.app"  # পরে বদলাবেন

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Webhook route
@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

# Health check route (Render এর জন্য)
@app.route('/health', methods=['GET'])
def health():
    return 'Bot is running', 200

# Root route
@app.route('/', methods=['GET'])
def index():
    return 'PP Digital Care Bot is running!', 200

# Command handlers
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "NoUsername"
    
    # Supabase এ ইউজার যোগ করুন
    url = f"{SUPABASE_URL}/rest/v1/users"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # চেক করুন ইউজার আগে আছে কিনা
    check_url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
    response = requests.get(check_url, headers=headers)
    
    if response.status_code == 200 and len(response.json()) == 0:
        data = {
            "id": user_id,
            "username": username,
            "balance": 0,
            "total_earned": 0,
            "created_at": datetime.now().isoformat()
        }
        requests.post(url, json=data, headers=headers)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎮 মিনি অ্যাপ খুলুন", web_app=WebAppInfo(url=WEBAPP_URL)))
    
    bot.send_message(
        message.chat.id,
        f"👋 স্বাগতম {username}!\n\n💰 আপনার ব্যালেন্স: $0\n\nনিচের বাটনে ক্লিক করে আয় শুরু করুন!",
        reply_markup=markup
    )

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}&select=balance"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        bal = response.json()[0]['balance']
        bot.reply_to(message, f"💰 আপনার ব্যালেন্স: ${bal}")
    else:
        bot.reply_to(message, "❌ ব্যালেন্স লোড করতে সমস্যা হয়েছে")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
