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
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# RIM CIFRLARINA ÓTKERIW FUNKCIYASI
# =========================
def to_roman(n):
    if not (0 < n < 4000): return None
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

# =========================
# TO'LIQ INFO TEXT (KR, RU, EN - Ózbekshe emes)
# =========================
INFO_TEXT = {
    "KR": """ITechnik — tárepinen islep shıgılģan 💫 kúshli programma járdeminde bot hárqanday esaptı mikron anıqlıģında esaplay aladı, bul bot Matematika, Ximiya hám Fizika pánleri ushun mólsherlengen.

👋😎 ITechnik 😎👉 Meniń menen baylanıs ushun: https://itechnik.taplink.ws""",

    "ru": """ITechnik — разработал 💫 мощную программу, с помощью которой бот может вычислять любые примеры с микронной точностью. Этот бот предназначен для математики, химии и физики.

👋😎 ITechnik 😎👉 Связь: https://itechnik.taplink.ws""",

    "en": """ITechnik — developed 💫 a powerful program that can calculate any example with micron accuracy. This bot is intended for Mathematics, Chemistry, and Physics.

👋😎 ITechnik 😎👉 Contact: https://itechnik.taplink.ws"""
}

# =========================
# JADVALLAR HÁM RIM CIFRLARI (KR, RU, EN)
# =========================
TABLES = {
    "math": {
        "KR": "➕ **Matematika:**\n• Kóbeytiw kestesi hám dárejeler.",
        "ru": "➕ **Математика:**\n• Таблица умножения и степени.",
        "en": "➕ **Math:**\n• Multiplication table and powers."
    },
    "fizika": {
        "KR": "🔭 **Fizika:**\n• Fizikalıq konstantalar hám formulalar.",
        "ru": "🔭 **Физика:**\n• Физические константы и формулы.",
        "en": "🔭 **Physics:**\n• Physical constants and formulas."
    },
    "ximiya": {
        "KR": "🧪 **Ximiya:**\n• Elementlerdiń periodikalıq sisteması.",
        "ru": "🧪 **Химия:**\n• Периодическая система элементов.",
        "en": "🧪 **Chemistry:**\n• Periodic table of elements."
    },
    "rim": {
        "KR": "🏛 **Rim cifrları:**\nI=1, V=5, X=10, L=50, C=100, D=500, M=1000\n\n💡 **Kórsetpe:** Maǵan qálegen butun san jiberiń, men onı Rim cifrına ótkerip beremen!",
        "ru": "🏛 **Римские цифры:**\nПришлите число, и я переведу его в римские цифры.",
        "en": "🏛 **Roman Numerals:**\nSend a number, and I will convert it to Roman numerals."
    }
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
    
    # Pánler hám Rim cifrları tugmaları
    menu_btns = {
        "KR": ["Matematika", "Fizika", "Ximiya", "Rim cifrları"],
        "ru": ["Математика", "Физика", "Химия", "Римские цифры"],
        "en": ["Math", "Physics", "Chemistry", "Roman Numerals"]
    }
    b = menu_btns[lang]
    keyboard = [
        [InlineKeyboardButton(f"🔢 {b[0]}", callback_data="tab_math"), InlineKeyboardButton(f"🔭 {b[1]}", callback_data="tab_fizika")],
        [InlineKeyboardButton(f"🧪 {b[2]}", callback_data="tab_ximiya"), InlineKeyboardButton(f"🏛 {b[3]}", callback_data="tab_rim")]
    ]
    
    await query.edit_message_text(INFO_TEXT[lang])
    
    msg = {"KR": "Endi maǵan esap jiberiń.", "ru": "Теперь отправьте пример.", "en": "Now send me an example."}
    await query.message.reply_text(msg[lang], reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "KR")
    if query.data.startswith("tab_"):
        key = query.data.split("_")[1]
        await query.message.reply_text(TABLES[key][lang], parse_mode="Markdown")

# =========================
# ESAPLAW HÁM RIM LOGIC
# =========================
async def handle_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    text = update.message.text.strip().lower()
    lang = context.user_data.get("lang", "KR")
    
    # Qaraqalpaqsha etiketkalar (Ózbekshe emes)
    res_labels = {"KR": "Juwap", "ru": "Результат", "en": "Result"}
    err_msgs = {
        "KR": "❌ Qatelik, iltimas esaptı durıs jazıń",
        "ru": "❌ Ошибка, пожалуйста, напишите пример правильно",
        "en": "❌ Error, please write the example correctly"
    }

    # 1. Rim cifrına ótkeriw
    if text.isdigit():
        num = int(text)
        roman = to_roman(num)
        if roman:
            rim_label = {"KR": "Rim cifrında", "ru": "В римских цифрах", "en": "In Roman numerals"}
            await update.message.reply_text(f"🏛 {rim_label[lang]}: {roman}")
            return

    # 2. Esaplaw
    try:
        expr = text.replace("×", "*").replace("÷", "/").replace("x", "*").replace(",", ".").replace("^", "**")
        safe_dict = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        result = eval(expr, {"__builtins__": None}, safe_dict)
        if isinstance(result, float):
            result = int(result) if result.is_integer() else round(result, 8)
        await update.message.reply_text(f"🧮 {res_labels[lang]}: {result}")
    except:
        await update.message.reply_text(err_msgs[lang])

def main():
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^tab_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_calculation))
    app.run_polling()

if __name__ == "__main__":
    main()

