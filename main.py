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
    bot.reply_to(message, "👋 বট সচল আছে! আপনার প্রশ্ন বা চার্ট পাঠান।")

@bot.message_handler(content_types=['text'])
def analyze_text(message):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=message.text
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "⚠️ সার্ভার ব্যস্ত, কিছুক্ষণ পর চেষ্টা করুন।")

@bot.message_handler(content_types=['photo'])
def analyze_photo(message):
    try:
        bot.reply_to(message, "🔍 চার্ট এনালাইসিস করা হচ্ছে...")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # সরাসরি সিম্পল প্রম্পট যাতে সার্ভারে লোড কম পড়ে
        prompt = "Analyze this binary trading chart. Give a short decision in Bengali: BUY, SELL, or WAIT with a brief reason."
        
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
        bot.reply_to(message, "⚠️ গুগল এপিআই ফ্রি লিমি트 বা সার্ভার ব্যস্ততার কারণে ছবিটি নিতে পারছে না। দয়া করে একটু পরে চেষ্টা করুন।")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
