import os
import telebot
from google import genai
from google.genai import types

# Render Environment Variables থেকে কী নেওয়া হচ্ছে
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client কনফিগারেশন
client = genai.Client(api_key=GEMINI_API_KEY)

# Telegram Bot কনফিগারেশন
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 ট্রেডিং সিগন্যাল বটে আপনাকে স্বাগতম! ট্রেডিং সংক্রান্ত প্রশ্ন অথবা চার্টের ছবি পাঠান, Gemini AI এনালাইসিস করে দেবে।")

# ১. টেক্সট মেসেজ প্রসেস করার জন্য
@bot.message_handler(content_types=['text'])
def analyze_text(message):
    try:
        prompt = f"You are an expert trading analyst. Analyze this query and give clear trading insight or signals: {message.text}"
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"একটি ত্রুটি ঘটেছে: {str(e)}")

# ২. ট্রেডিং চার্টের ছবি প্রসেস করার জন্য
@bot.message_handler(content_types=['photo'])
def analyze_photo(message):
    try:
        bot.reply_to(message, "🔍 আপনার চার্টের ছবি অ্যানালাইসিস করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")
        
        # সবচেয়ে ভালো কোয়ালিটির ছবিটি নেওয়া হচ্ছে
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        prompt = "You are an expert trading analyst. Analyze this trading chart image carefully. Identify current trend, support/resistance levels, indicators (like EMA, RSI if visible), and give clear signal or market insight in Bengali."
        
        # Gemini API-তে ছবি ও প্রম্পট পাঠানো
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[
                types.Part.from_bytes(
                    data=downloaded_file,
                    mime_type="image/jpeg"
                ),
                prompt
            ]
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"ছবি বিশ্লেষণ করতে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    bot.infinity_polling()
