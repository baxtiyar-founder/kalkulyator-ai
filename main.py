import os
import sys
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================
# BOT SOZLAMALARI
# =========================
# Yangi tokenni Render dashboard'idagi BOT_TOKEN katagiga yozing.
# Kod esa uni avtomatik ravishda o'qib oladi.
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# TO'LIQ INFO TEXT
# =========================
INFO_TEXT = {
    "KR": """ITechnik — tárepinen islep shıgılģan 💫 kúshli programma járdeminde bot hárqanday esaptı mikron anıqlıģında esaplay aladı, bul bot Matematika, Ximiya hám Fizika pánleri ushun mólsherlengen. Botqa belgili waqt ishinde jańa premium funksiyalar qosıladı hámde jaqsılanadı.
    
👋😎 ITechnik 😎👉 Meniń menen baylanıs ushun: https://itechnik.taplink.ws""",

    "ru": """ITechnik — разработал 💫 мощную программу, с помощью которой бот может вычислять любые примеры с микронной точностью. Этот бот предназначен для математики, химии и физики. 

👋😎 ITechnik 😎👉 Связь: https://itechnik.taplink.ws""",

    "en": """ITechnik — developed 💫 a powerful program that can calculate any example with micron accuracy. This bot is intended for Mathematics, Chemistry, and Physics. 

👋😎 ITechnik 😎👉 Contact: https://itechnik.taplink.ws"""
}

# =========================
# START & LANGUAGE
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("RU  Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("EN  English", callback_data="lang_en")],
        [InlineKeyboardButton("KR  Qaraqalpaq tili", callback_data="lang_KR")]
    ]
    await update.message.reply_text(
        "Tildi tańlań / Выберите язык / Choose a language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    
    await query.edit_message_text(INFO_TEXT[lang])
    
    msg = "Endi maģan esap jiberiń (máselen: 2+2×3)."
    if lang == "ru": msg = "Теперь отправьте пример (например: 2+2×3)."
    if lang == "en": msg = "Now send me an example (e.g.: 2+2×3)."
    
    await query.message.reply_text(msg)

# =========================
# KALKULYATOR LOGIC
# =========================
async def handle_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    text = update.message.text.strip()
    
    try:
        safe_dict = {
            "math": math,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e, "pow": math.pow
        }
        eval_text = text.replace('×', '*').replace('x', '*').replace('÷', '/').replace(',', '.')
        
        result = eval(eval_text, {"__builtins__": None}, safe_dict)
        
        await update.message.reply_text(f"Natija / Результат / Result: {result}")
    except Exception:
        pass

# =========================
# MAIN
# =========================
def main():
    # Tokenni tekshirish
    if not BOT_TOKEN:
        print("XATO: BOT_TOKEN topilmadi. Render Environment Variables bo'limini tekshiring!")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(choose_language, pattern="^lang_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_calculation))

    print("✅️ Bot ishga tushdi")
    application.run_polling()

if __name__ == "__main__":
    main()

