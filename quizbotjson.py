import json
import io
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8424951624:AAH5kqadTIofTAAZsRgwZTQkU-2hqjW7niQ"

sessions = {}  # key: chat_id, value: list of quizzes

# /baslayiriq komandası
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sessions[chat_id] = []
    await update.message.reply_text("Quiz seansı başladı! Quiz-ləri göndərə bilərsən.")

# /bitirdik komandası - fayl şəklində JSON göndərir
async def end_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sessions or len(sessions[chat_id]) == 0:
        await update.message.reply_text("Heç bir quiz göndərilməyib.")
        return

    json_str = json.dumps(sessions[chat_id], ensure_ascii=False, indent=2)
    # JSON mətnini fayla çeviririk (in-memory)
    bio = io.BytesIO()
    bio.write(json_str.encode('utf-8'))
    bio.seek(0)  # faylın əvvəlindən oxumağa hazırla

    # Telegram-da sənəd kimi göndər
    await update.message.reply_document(document=bio, filename="quiz.json")

    sessions[chat_id] = []  # session-u sıfırla

# Poll mesajlarını JSON-a çevirən funksiya
async def handle_poll_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in sessions:
        await update.message.reply_text("Quiz seansı başlamayıb. /baslayiriq yazın.")
        return

    poll = update.message.poll
    question_text = re.sub(r"^\[\d+/\d+\]\s*", "", poll.question)

    options = {chr(97 + i): opt.text for i, opt in enumerate(poll.options)}
    correct_index = poll.correct_option_id
    correct_key = chr(97 + correct_index) if correct_index is not None else None

    quiz_json = {
        "type": "SINGLE_CHOICE",
        "questionText": question_text,
        "options": options,
        "correctAnswer": correct_key
    }

    sessions[chat_id].append(quiz_json)
    await update.message.reply_text("Quiz əlavə edildi ✅")

# Bot qurulması
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("baslayiriq", start_quiz))
app.add_handler(CommandHandler("bitirdik", end_quiz))
app.add_handler(MessageHandler(filters.POLL, handle_poll_message))

print("Bot işə düşdü...")
app.run_polling()
