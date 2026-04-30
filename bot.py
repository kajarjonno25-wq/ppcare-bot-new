from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import os

app = Flask(__name__)

BOT_TOKEN = "8683913109:AAGqeL4FleykAuOIoqeoSFQ77H4pryBewG4"
WEBAPP_URL = "https://pp-miniapp-8q97.vercel.app"

bot = telebot.TeleBot(BOT_TOKEN)

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return 'Bot is running'

@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎮 মিনি অ্যাপ খুলুন", web_app=WebAppInfo(url=WEBAPP_URL)))
    bot.send_message(message.chat.id, "👋 স্বাগতম! নিচের বাটনে ক্লিক করুন", reply_markup=markup)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
