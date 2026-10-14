import os
import telebot
from openai import OpenAI

# Render Environment Variables থেকে টোকেনগুলো নেওয়া হচ্ছে
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAI Client কনফিগারেশন (খוד স্থিতিশীল ও ফাস্ট)
client = OpenAI(api_key=OPENAI_API_KEY)

# Telegram Bot কনফিগারেশন
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 ট্রেডিং বট সক্রিয় রয়েছে! চার্টের ছবি পাঠান, সরাসরি সংক্ষেপে BUY / SELL / WAIT সিগন্যাল পেয়ে যাবেন।")

# ১. টেক্সট মেসেজ প্রসেস করার জন্য
@bot.message_handler(content_types=['text'])
def analyze_text(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional binary and forex trading analyst. Reply strictly in Bengali with a short, direct trading decision (BUY, SELL, or WAIT) and a brief reason."},
                {"role": "user", "content": message.text}
            ]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"একটি ত্রুটি ঘটেছে: {str(e)}")

# ২. ট্রেডিং চার্টের ছবি প্রসেস করার জন্য (সরাসরি সিগন্যাল)
@bot.message_handler(content_types=['photo'])
def analyze_photo(message):
    try:
        bot.reply_to(message, "🔍 আপনার চার্ট বিশ্লেষণ করা হচ্ছে...")
        
        # টেলিগ্রাম থেকে ছবি ডাউনলোড করার লিংক নেওয়া
        file_info = bot.get_file(message.photo[-1].file_id)
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert binary and forex trading analyst. Analyze the provided chart image and output the result strictly in Bengali following this short format:\n\n🔴/🟢/🟡 **সিদ্ধান্ত (Decision):** [BUY / SELL / WAIT]\n🎯 **কনফিডেন্স (Confidence):** [e.g. 85%]\n⏱ **মেয়াদ/টাইমফ্রেম:** [e.g. 1 Minute]\n\n📌 **সংক্ষিপ্ত কারণ:**\n- [ট্রেন্ড বা সাপোর্ট/রেজিস্ট্যান্সের সংক্ষিপ্ত ব্যাখ্যা]\n- [ইন্ডিকেটর যেমন RSI বা মুভিং এভারেজের অবস্থা]"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this trading chart and give a quick signal:"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=300
        )
        
        bot.reply_to(message, response.choices[0].message.content)

    except Exception as e:
        bot.reply_to(message, f"ছবি বিশ্লেষণ করতে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    bot.infinity_polling()
