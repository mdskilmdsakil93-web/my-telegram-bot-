import os
import telebot
from google import genai
from google.genai import types

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 ট্রেডিং বট সক্রিয়! চার্টের ছবি পাঠান, সরাসরি সিগন্যাল দেওয়া হবে।")

@bot.message_handler(content_types=['text'])
def analyze_text(message):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"You are a trading analyst. Reply strictly in Bengali with a short decision (BUY, SELL, or WAIT) and reason for: {message.text}"
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "⚠️ সার্ভার ব্যস্ত রয়েছে, অনুগ্রহ করে আবার চেষ্টা করুন।")

@bot.message_handler(content_types=['photo'])
def analyze_photo(message):
    try:
        bot.reply_to(message, "🔍 আপনার চার্ট বিশ্লেষণ করা হচ্ছে...")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        prompt = """
Analyze this binary trading chart and output strictly in Bengali in this short format:

🔴/🟢/🟡 **সিদ্ধান্ত:** [BUY / SELL / WAIT]
🎯 **কনফিডেন্স:** [যেমন: 80%]
📌 **সংক্ষিপ্ত কারণ:** [১ লাইনে কারণ]
"""
        
        image_part = types.Part.from_bytes(
            data=downloaded_file,
            mime_type="image/jpeg"
        )
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[image_part, prompt]
        )
        bot.reply_to(message, response.text)

    except Exception as e:
        bot.reply_to(message, "⚠️ ছবি বিশ্লেষণ করতে সমস্যা হয়েছে। দয়া করে আবার পাঠান।")

if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    bot.infinity_polling()
