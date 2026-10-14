import os
import telebot
import requests
import base64

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 ট্রেডিং বট সচল রয়েছে! চার্টের ছবি পাঠান, সরাসরি সিগন্যাল দেওয়া হবে।")

@bot.message_handler(content_types=['text'])
def analyze_text(message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": f"You are a trading analyst. Reply strictly in Bengali with a short decision (BUY, SELL, or WAIT) and reason for: {message.text}"}]
            }]
        }
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        answer = res_json['candidates'][0]['content']['parts'][0]['text']
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, "⚠️ সার্ভার ব্যস্ত রয়েছে, কিছুক্ষণ পর চেষ্টা করুন।")

@bot.message_handler(content_types=['photo'])
def analyze_photo(message):
    try:
        bot.reply_to(message, "🔍 আপনার চার্ট বিশ্লেষণ করা হচ্ছে...")
        
        # টেলিগ্রাম থেকে ছবি ডাউনলোড করা
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # ছবিকে Base64 ফরম্যাটে রূপান্তর
        encoded_image = base64.b64encode(downloaded_file).decode('utf-8')

        prompt = """
Analyze this binary trading chart and output strictly in Bengali in this short format:

🔴/🟢/🟡 **সিদ্ধান্ত:** [BUY / SELL / WAIT]
🎯 **কনফিডেন্স:** [যেমন: 80%]
📌 **সংক্ষিপ্ত কারণ:** [১ লাইনে কারণ]
"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        
        if 'candidates' in res_json:
            answer = res_json['candidates'][0]['content']['parts'][0]['text']
            bot.reply_to(message, answer)
        else:
            bot.reply_to(message, f"⚠️ এপিআই রেসপন্স এরর: {res_json.get('error', {}).get('message', 'Unknown error')}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ ছবি বিশ্লেষণ করতে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.remove_webhook()
    bot.infinity_polling()
