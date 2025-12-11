import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import google.generativeai as genai
from flask import Flask
from threading import Thread

# ----------------- CONFIGURATION -----------------
# Environment Variables (Render မှာ ထည့်ရမည့် တန်ဖိုးများ)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_ID = os.getenv("ADMIN_ID") # အစ်ကို့ရဲ့ Numeric ID (User ID) ကိုထည့်ရပါမယ်

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Course Context (အစ်ကိုပေးထားတဲ့ အချက်အလက်များ)
COURSE_CONTEXT = """
Role: You are "Burma Ai", a helpful assistant for the course "The Digital Canvas".
Course Name: The Digital Canvas
Price: 50,000 MMK (Lifetime access)

Course Content (What students will learn):
1. Nanobanana AI: Basic to advanced usage & templates.
2. Gemini AI: Basic usage guide.
3. Prompt Engineering: How to control AI effectively.
4. Notebook LM: Full guide.
5. Chatbot Creation: Building custom chatbots (Gem) for personal or business use.
6. Social Media Design: Using AI for design.
7. Comic Book Creation: Creating comic books using AI.
8. Telegram Bot Creation: Building AI-powered telegram bots.

Benefits:
- Beginner friendly.
- Lifetime access & future updates.
- Direct Admin support (Online/Phone) if stuck.
- Great for those wanting to earn income with AI.

Payment Channels:
- Kpay: 09667566483
- Wave: 09781964430
- AYA Pay: 09667566483

Admin Contact: @Leolanses
Instruction: Answer questions nicely in Burmese. If asked about price or registration, guide them to use the menu buttons.
"""

# Registration States
NAME, PHONE, SLIP = range(3)

# ----------------- WEB SERVER (24/7 Run) -----------------
app = Flask('')
@app.route('/')
def home():
    return "Burma Ai is Alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------------- BOT FUNCTIONS -----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    welcome_msg = (
        f"မင်္ဂလာပါ {user} ခင်ဗျာ! 👋\n"
        "**The Digital Canvas** Course ရဲ့ Official Bot 'Burma Ai' မှ ကြိုဆိုပါတယ်။\n\n"
        "ကျွန်တော်က AI နည်းပညာ၊ Prompt Engineering နဲ့ Bot တည်ဆောက်နည်းတွေကို "
        "အခြေခံကနေ စီးပွားဖြစ်အထိ ကူညီပေးမယ့် Assistant ဖြစ်ပါတယ်။\n\n"
        "သိလိုတာများကို အောက်ပါ Menu မှာ နှိပ်ကြည့်နိုင်သလို၊ စာရိုက်ပြီးလည်း မေးမြန်းနိုင်ပါတယ်ခင်ဗျာ။ 👇"
    )
    
    # Menu Buttons
    buttons = [
        [KeyboardButton("Course Info 📚"), KeyboardButton("Price & Payment 💰")],
        [KeyboardButton("Register 📝"), KeyboardButton("Contact Admin 👨‍💻")],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode='Markdown')

# --- MENU HANDLER ---
async def handle_menu_and_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Course Info 📚":
        info_msg = (
            "🚀 **The Digital Canvas Course အကြောင်း**\n\n"
            "ဒီသင်တန်းမှာ ဘာတွေသင်မှာလဲဆိုတော့ -\n"
            "1️⃣ Nanobanana AI (Basic to Advanced)\n"
            "2️⃣ Gemini AI အသုံးပြုနည်း\n"
            "3️⃣ Prompt Engineering (AI ကို ကျွမ်းကျင်စွာ ခိုင်းစေနည်း)\n"
            "4️⃣ Notebook LM Full Guide\n"
            "5️⃣ Custom Chatbot (Gem) တည်ဆောက်နည်း\n"
            "6️⃣ AI Social Media Design ရေးဆွဲနည်း\n"
            "7️⃣ AI Comic Book (ရုပ်ပြ) ဖန်တီးနည်း\n"
            "8️⃣ AI Telegram Bot ဖန်တီးနည်း (Business/Personal)\n\n"
            "✅ Lifetime Access ဖြစ်ပြီး Update အသစ်တွေလည်း အလကားရမှာပါ။\n"
            "✅ Beginner တန်းမို့ အခြေခံမရှိလည်း တက်လို့ရပါတယ်။"
        )
        await update.message.reply_text(info_msg)

    elif text == "Price & Payment 💰":
        pay_msg = (
            "💰 **သင်တန်းကြေး - 50,000 ကျပ်** (Lifetime)\n\n"
            "ငွေလွှဲရန် အကောင့်များ -\n"
            "✅ **Kpay:** `09667566483`\n"
            "✅ **Wave:** `09781964430`\n"
            "✅ **AYA:** `09667566483`\n\n"
            "သင်တန်းအပ်မယ်ဆိုရင် **Register** ခလုတ်ကို နှိပ်လိုက်ပါ။ 👇"
        )
        await update.message.reply_text(pay_msg, parse_mode='Markdown')

    elif text == "Contact Admin 👨‍💻":
        await update.message.reply_text(
            "Admin နဲ့ တိုက်ရိုက်ဆွေးနွေးလိုပါက ဒီအကောင့်ကို ဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ။\n👉 @Leolanses"
        )

    elif text == "Register 📝":
        # Conversation Handler will catch the command instead usually, 
        # but here we trigger via text. We handle this in main handler logic basically.
        # But properly, we use EntryPoints. Since this is text, we need a trick or just ask user to click /register command
        # For simplicity in this code structure, I will redirect to the conversation start directly below.
        pass 

    else:
        # AI Chat Response
        try:
            chat_session = model.start_chat(history=[])
            prompt = f"{COURSE_CONTEXT}\n\nUser asked: {text}\nAnswer in Burmese:"
            response = chat_session.send_message(prompt)
            await update.message.reply_text(response.text)
        except Exception:
            await update.message.reply_text("Server error လေးဖြစ်နေလို့ ခဏနေမှ ပြန်မေးပေးပါခင်ဗျာ။")

# --- REGISTRATION SYSTEM ---
async def start_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 **သင်တန်းအပ်နှံခြင်း**\n\n"
        "ပထမဆုံးအနေနဲ့ မိတ်ဆွေရဲ့ **နာမည်** လေး ရေးပေးပါခင်ဗျာ။"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("ဟုတ်ကဲ့၊ ဆက်သွယ်ရမယ့် **ဖုန်းနံပါတ်** လေး ပေးပါခင်ဗျာ။")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "ကျေးဇူးပါ၊ Kpay/Wave/AYA သို့ ငွေလွှဲထားသော **Screenshot** (ငွေလွှဲပြေစာ) လေး ပို့ပေးပါခင်ဗျာ။"
    )
    return SLIP

async def get_slip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    
    # Message to Admin
    admin_msg = (
        f"🚀 **New Course Order!**\n"
        f"👤 Name: {context.user_data['name']}\n"
        f"📞 Phone: {context.user_data['phone']}\n"
        f"🔗 Telegram: @{user.username} ({user.id})"
    )
    
    # Send to Admin if ID is set
    if ADMIN_ID:
        try:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_file.file_id, caption=admin_msg)
            await update.message.reply_text("✅ အချက်အလက်များ လက်ခံရရှိပါတယ်။ Admin မှ စစ်ဆေးပြီး သင်တန်း Group ထဲ ချက်ချင်း ထည့်ပေးပါမယ်ခင်ဗျာ။")
        except Exception as e:
            await update.message.reply_text("✅ လက်ခံရရှိပါတယ်။ (Admin သို့ ပို့မရပါ - ID စစ်ဆေးပါ)")
    else:
        await update.message.reply_text("✅ လက်ခံရရှိပါတယ်။ Admin မှ မကြာမီ ဆက်သွယ်ပါမယ်။")
        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration ကို ပယ်ဖျက်လိုက်ပါပြီ။")
    return ConversationHandler.END

# ----------------- MAIN EXECUTION -----------------
if __name__ == '__main__':
    keep_alive()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Registration Flow
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('register', start_register),
            MessageHandler(filters.Regex('^Register 📝$'), start_register) # Button click triggers register
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SLIP: [MessageHandler(filters.PHOTO, get_slip)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    
    # General Message Handler (Must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_and_ai))

    print("Burma Ai is running...")
    app.run_polling()