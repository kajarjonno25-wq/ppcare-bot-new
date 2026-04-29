from fastapi import FastAPI, Request, Response
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import requests
from datetime import datetime
import os
import uvicorn

app = FastAPI()

BOT_TOKEN = "8683913109:AAGqeL4FleykAuOIoqeoSFQ77H4pryBewG4"
SUPABASE_URL = "https://kzvnwugoyqbyxslxzzul.supabase.co"
SUPABASE_KEY = "sb_publishable_OlsWkOtI5JjJ0UBZLqsP8Q_T4kS3xsG"
WEBAPP_URL = "https://kzvnwugoyqbyxslxzzul.supabase.co"

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request):
    json_str = await request.body()
    update = telebot.types.Update.de_json(json_str.decode('utf-8'))
    bot.process_new_updates([update])
    return Response(content="OK", status_code=200)

@app.get("/")
async def index():
    return {"message": "PP Digital Care Bot is running!"}

@app.get("/health")
async def health():
    return {"status": "alive"}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "NoUsername"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    check_url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}"
    try:
        response = requests.get(check_url, headers=headers)
        if response.status_code == 200 and len(response.json()) == 0:
            data = {
                "id": user_id,
                "username": username,
                "balance": 0,
                "total_earned": 0,
                "created_at": datetime.now().isoformat()
            }
            requests.post(f"{SUPABASE_URL}/rest/v1/users", json=data, headers=headers)
    except Exception as e:
        print(f"Supabase error: {e}")
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎮 মিনি অ্যাপ খুলুন", web_app=WebAppInfo(url=WEBAPP_URL)))
    
    bot.send_message(message.chat.id, f"👋 স্বাগতম {username}!\n\n💰 আপনার ব্যালেন্স: $0\n\nনিচের বাটনে ক্লিক করে আয় শুরু করুন!", reply_markup=markup)

@bot.message_handler(commands=['balance'])
def balance(message):
    user_id = str(message.from_user.id)
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}&select=balance"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            bal = response.json()[0]['balance']
            bot.reply_to(message, f"💰 আপনার ব্যালেন্স: ${bal}")
        else:
            bot.reply_to(message, "❌ ব্যালেন্স লোড করতে সমস্যা হয়েছে")
    except Exception as e:
        bot.reply_to(message, f"❌ এরর: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
