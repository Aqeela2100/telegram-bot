from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import sqlite3

TOKEN = "8116954770:AAHqJYnGLjoE-WFngrCQhRjHMDs-Z1zx1BE"
SECRET = "mysecret12345"   # غيرها لو تحب
DB_PATH = "app.db"

# ===== البحث في قاعدة البيانات =====
def search_student(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, grade, paid, remaining, phone, branch, year, notes, status
        FROM students
        WHERE name LIKE ? OR phone LIKE ?
    """, ('%' + query + '%', '%' + query + '%'))

    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    name, grade, paid, remaining, phone, branch, year, notes, status = result
    message = (
        f"📌 *معلومات الطالب*\n"
        f"————————————\n"
        f"👤 الاسم: {name}\n"
        f"🏫 الصف: {grade}\n"
        f"💰 المبلغ المدفوع: {paid}\n"
        f"💸 المتبقي: {remaining}\n"
        f"📞 رقم الموبايل: {phone}\n"
        f"📍 الفرع: {branch}\n"
        f"📅 السنة الدراسية: {year}\n"
        f"📝 الملاحظات: {notes}\n"
        f"⚡ الحالة: {status}"
    )
    return message

# ===== رد البوت =====
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    student_data = search_student(query)

    if student_data:
        await update.message.reply_text(student_data, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لم يتم العثور على الطالب.")

# ===== Telegram Bot Setup =====
telegram_app = ApplicationBuilder().token(TOKEN).build()
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# ===== Flask Webhook =====
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running."

@flask_app.route(f"/{SECRET}", methods=["POST"])
async def webhook():
    data = request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return "OK"

# ===== تشغيل Flask فقط (Render) =====
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=10000)
