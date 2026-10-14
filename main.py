import os
import time
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

# 503 বা হাই ডিমান্ড এরর এড়াতে বিভিন্ন মডেলের তালিকা
MODELS_TO_TRY = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash"]

def call_gemini_with_retry(contents):
    """সার্ভার ব্যস্ত থাকলে ঘুরেফিরে বিভিন্ন মডেল দিয়ে চেষ্টা করার ফাংশন"""
    last_error = None
    for model in MODELS_TO_TRY:
        for attempt in range(2): # প্রতি মডেলে ২ বার ট্রাই করবে
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                time.sleep(1) # ১ সেকেন্ড অপেক্ষা করে আবার চেষ্টা করবে
                continue
    raise last_error

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 ট্রেডিং বট সক্রিয় রয়েছে! চার্টের ছবি পাঠান, সরাসরি সিগন্যাল পেয়ে যাবেন।")

# ১. টেক্সট মেসেজ প্রসেস করার জন্য
@bot.message_handler(content_types=['text'])
def analyze_text(message):
    try:
        prompt = f"You are a professional trading analyst. Respond strictly in Bengali. User query: {message.text}. Give a direct decision: BUY, SELL, or WAIT with short reason."
        answer = call_gemini_with_retry(prompt)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, "⚠️ সার্ভারে অতিরিক্ত ব্যস্ততা (High Demand) রয়েছে। অনুগ্রহ করে আর একবার ছবিটি বা টেক্সটটি পাঠান।")

# ২. ট্রেডিং চার্টের ছবি প্রসেস করার জন্য
@bot.message_handler(content_types=['photo'])
def analyze_photo(message):
    try:
        bot.reply_to(message, "🔍 আপনার চার্ট নিখুঁতভাবে বিশ্লেষণ করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        prompt = """
You are an expert binary and forex trading analyst. Analyze this chart image and output the result strictly in Bengali in this short format:

🔴/🟢/🟡 **সিদ্ধান্ত (Decision):** [BUY / SELL / WAIT]
🎯 **কনফিডেন্স (Confidence):** [e.g. 80%]
⏱ **মেয়াদ/টাইমফ্রেম:** [e.g. 1 Minute]

📌 **সংক্ষিপ্ত কারণ:**
- [ট্রেন্ড ও সাপোর্ট/রেজিস্ট্যান্সের সংক্ষিপ্ত ব্যাখ্যা]
- [ইন্ডিকেটর যেমন RSI এর অবস্থা]

⚠️ **সতর্কতা:** [ঝুঁকি ব্যবস্থাপনা সম্পর্কিত ১ লাইন]
"""
        
        image_part = types.Part.from_bytes(
            data=downloaded_file,
            mime_type="image/jpeg"
        )
        
        answer = call_gemini_with_retry([image_part, prompt])
        bot.reply_to(message, answer)

    except Exception as e:
        bot.reply_to(message, "⚠️ গুগল এপিআই সার্ভারে অতিরিক্ত ট্রাফিকের কারণে সাময়িকভাবে সমস্যা হচ্ছে। দয়া করে ১০-১৫ সেকেন্ড পর আবার ছবিটি পাঠিয়ে ট্রাই করুন।")

if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    bot.infinity_polling()
