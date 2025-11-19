from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import asyncio
import sqlite3

TOKEN = "8116954770:AAHqJYnGLjoE-WFngrCQhRjHMDs-Z1zx1BE"
SECRET = "mysecret12345"
DB_PATH = "app.db"

# ================== DATABASE ==================
def search_student(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, grade, paid, remaining, phone, branch, year, notes, status
        FROM students
        WHERE name LIKE ? OR phone LIKE ?
    """, (f"%{query}%", f"%{query}%"))

    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    name, grade, paid, remaining, phone, branch, year, notes, status = result
    return (
        f"📌 *معلومات الطالب*\n"
        f"————————————\n"
        f"👤 الاسم: {name}\n"
        f"🏫 الصف: {grade}\n"
        f"💰 المدفوع: {paid}\n"
        f"💸 المتبقي: {remaining}\n"
        f"📞 الرقم: {phone}\n"
        f"📍 الفرع: {branch}\n"
        f"📅 السنة: {year}\n"
        f"📝 الملاحظات: {notes}\n"
        f"⚡ الحالة: {status}"
    )

# ================== BOT HANDLER ==================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    query = update.message.text
    result = search_student(query)

    if result:
        await update.message.reply_text(result, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لم يتم العثور على الطالب.")

# Create Telegram Bot
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# Create Flask App
flask_app = Flask(__name__)

@flask_app.get("/")
def home():
    return "Bot is running!"

@flask_app.post(f"/{SECRET}")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

# ================== START ==================
if __name__ == "__main__":
    # تشغيل Flask فقط
    flask_app.run(host="0.0.0.0", port=10000)
