from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import sqlite3
import os
from asyncio import run_coroutine_threadsafe

TOKEN = "7974041535:AAGhCBD1rlD6N9AW4faKOeRLtj0ROIj18Xw"
SECRET = "mysecret12345"  # يمكنك تغييره
DB_PATH = "app.db"

# ================== DATABASE ==================
def search_students(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, grade, paid, remaining, phone, branch, year, notes, status
        FROM students
        WHERE name LIKE ? OR phone LIKE ?
    """, ('%' + query + '%', '%' + query + '%'))
    results = cursor.fetchall()
    conn.close()
    return results

def format_student_message(student):
    name, grade, paid, remaining, phone, branch, year, notes, status = student
    return (
        f"📌 *معلومات الطالب*\n"
        f"————————————\n"
        f"👤 الاسم: {name}\n"
        f"🏫 الصف: {grade}\n"
        f"💰 المبلغ المدفوع: {paid}\n"
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
    query = update.message.text.strip()
    students = search_students(query)
    if students:
        for student in students:
            message = format_student_message(student)
            await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لم يتم العثور على الطالب.")

# ================== TELEGRAM BOT ==================
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# ================== FLASK APP ==================
flask_app = Flask(__name__)

@flask_app.get("/")
def home():
    return "Bot is running!"

@flask_app.post(f"/{SECRET}")
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    # معالجة async بشكل صحيح على Flask
    run_coroutine_threadsafe(telegram_app.process_update(update), telegram_app.bot.loop)
    return "OK"

# ================== START ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)
