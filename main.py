import os
import telebot
from google import genai

# Render Environment Variables থেকে কী নেওয়া হচ্ছে
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client কনফিগারেশন
client = genai.Client(api_key=GEMINI_API_KEY)

# Telegram Bot কনফিগারেশন
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 ট্রেডিং সিগন্যাল বটে আপনাকে স্বাগতম! আপনার ট্রেডিং প্রশ্ন বা ডেটা পাঠান, Gemini AI অ্যানালাইসিস করে দেবে।")

@bot.message_handler(func=lambda message: True)
def analyze_trading(message):
    try:
        # Gemini API দিয়ে ট্রেডিং এনালাইসিস
        prompt = f"You are an expert trading analyst. Analyze this query and give clear trading insight or signals: {message.text}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"একটি ত্রুটি ঘটেছে: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
