import os
import telebot
from google import genai
from google.genai import types

# Render Environment Variables থেকে কী নেওয়া হচ্ছে
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client কনফিগারেশন
client = genai.Client(api_key=GEMINI_API_KEY)

# Telegram Bot কনফিগারেশন
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 503 এরর এড়াতে একাধিক মডেলের ফলব্যাক লিস্ট
AVAILABLE_MODELS = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-1.5-pro"]

def generate_gemini_response(contents):
    """সার্ভার ওভারলোড এড়াতে পর্যায়ক্রমে কাজ করার ফাংশন"""
    for model_name in AVAILABLE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e) or "404" in str(e):
                continue
            raise e
    raise Exception("গুগল এপিআই সার্ভার ব্যস্ত রয়েছে। অনুগ্রহ করে কয়েক সেকেন্ড পর আবার চেষ্টা করুন।")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 ট্রেডিং সিগন্যাল বটে আপনাকে স্বাগতম! চার্টের ছবি পাঠান, সরাসরি BUY / SELL / WAIT সিগন্যাল পাবেন।")

# ১. টেক্সট মেসেজ প্রসেস করার জন্য
@bot.message_handler(content_types=['text'])
def analyze_text(message):
    try:
        prompt = f"You are a strict trading analyst. Respond strictly in Bengali. User text: {message.text}. Give a direct, short answer with clear decision: BUY, SELL, or WAIT, along with brief reasoning."
        answer = generate_gemini_response(prompt)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"একটি ত্রুটি ঘটেছে: {str(e)}")

# ২. ট্রেডিং চার্টের ছবি প্রসেস করার জন্য (সরাসরি সিগন্যাল প্রম্পট)
@bot.message_handler(content_types=['photo'])
def analyze_photo(message):
    try:
        bot.reply_to(message, "🔍 আপনার চার্ট বিশ্লেষণ করা হচ্ছে...")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # সংক্ষিপ্ত ও নিখুঁত সিগন্যালের জন্য কাস্টম প্রম্পট
        prompt = """
You are an expert binary option / forex trading analyst. Analyze this chart image quickly and strictly output the response in Bengali following this EXACT short structure:

🔴/🟢/🟡 **সিদ্ধান্ত (Decision):** [BUY / SELL / WAIT]
🎯 **কনফিডেন্স (Confidence):** [e.g. 85%]
⏱ **টাইমফ্রেম/মেয়াদ:** [e.g. 1 Minute / Next Candle]

📌 **সংক্ষিপ্ত কারণ (Reason):**
- [১ লাইনে ট্রপ/ট্রেন্ড বা সাপোর্ট/রেজিস্ট্যান্স কারণ]
- [১ লাইনে ইন্ডিকেটর যেমন RSI / Moving Average অবস্থা]

⚠️ **পরামর্শ:** [সংক্ষেপে ১ লাইনে ঝুঁকি বা সতর্কবার্তা]
"""
        
        image_part = types.Part.from_bytes(
            data=downloaded_file,
            mime_type="image/jpeg"
        )
        
        answer = generate_gemini_response([image_part, prompt])
        bot.reply_to(message, answer)

    except Exception as e:
        bot.reply_to(message, f"ছবি বিশ্লেষণ করতে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    bot.infinity_polling()
