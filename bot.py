"""Telegram owner bot. Set BOT_TOKEN and OWNER_TELEGRAM_ID in environment."""
import os, logging, httpx
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from backend.config import settings
from backend.ai import answer
from backend.database import Base, engine, SessionLocal
from backend.models import Task, Note

logging.basicConfig(level=logging.INFO)
KEYBOARD=ReplyKeyboardMarkup([["💬 AI Chat","📋 Tasks"],["📝 Save Note","❓ Help"]],resize_keyboard=True)
def allowed(update): return bool(update.effective_user and settings.owner_telegram_id and update.effective_user.id==settings.owner_telegram_id)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await update.message.reply_text("দুঃখিত, এই বটটি অনুমোদিত মালিকের জন্য।")
    await update.message.reply_text("দোস্ত, Personal AI Agent MVP চালু আছে। /help লিখে কমান্ড দেখো।",reply_markup=KEYBOARD)
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await update.message.reply_text("Access denied.")
    await update.message.reply_text("/chat তোমার প্রশ্ন\n/task কাজ যোগ করো\n/note নোট সেভ করো\n/tasks টাস্ক দেখো\n\nবট এখনো ফোনে স্বয়ংক্রিয়ভাবে কাজ চালায় না; উচ্চ-প্রভাবের কাজ নিজে থেকে করবে না।")
async def chat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await update.message.reply_text("Access denied.")
    msg=" ".join(context.args).strip()
    if not msg: return await update.message.reply_text("ব্যবহার: /chat তোমার প্রশ্ন")
    await update.message.reply_text(await answer(msg))
async def task_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await update.message.reply_text("Access denied.")
    title=" ".join(context.args).strip()
    if not title: return await update.message.reply_text("ব্যবহার: /task আজকের কাজ শেষ করা")
    db=SessionLocal()
    try:
        t=Task(owner_id=str(update.effective_user.id),title=title,status="pending"); db.add(t); db.commit(); db.refresh(t)
        await update.message.reply_text(f"টাস্ক সেভ হয়েছে #{t.id}: {t.title}")
    finally: db.close()
async def tasks_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await update.message.reply_text("Access denied.")
    db=SessionLocal()
    try: rows=db.query(Task).filter_by(owner_id=str(update.effective_user.id)).order_by(Task.id.desc()).limit(20).all()
    finally: db.close()
    await update.message.reply_text("📋 তোমার টাস্ক:\n" + ("\n".join(f"#{t.id} [{t.status}] {t.title}" for t in rows) if rows else "এখনো কোনো টাস্ক নেই।"))
async def note_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await update.message.reply_text("Access denied.")
    content=" ".join(context.args).strip()
    if not content: return await update.message.reply_text("ব্যবহার: /note এই নোটটি মনে রাখো")
    db=SessionLocal()
    try: db.add(Note(owner_id=str(update.effective_user.id),content=content)); db.commit()
    finally: db.close()
    await update.message.reply_text("📝 নোট সেভ হয়েছে।")
async def text_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update): return await update.message.reply_text("Access denied.")
    txt=update.message.text or ""
    if txt=="📋 Tasks": return await tasks_cmd(update,context)
    if txt=="❓ Help": return await help_cmd(update,context)
    await update.message.reply_text(await answer(txt))
def main():
    if not settings.bot_token: raise SystemExit("BOT_TOKEN missing")
    if not settings.owner_telegram_id: raise SystemExit("OWNER_TELEGRAM_ID missing")
    Base.metadata.create_all(bind=engine)
    app=Application.builder().token(settings.bot_token).build()
    app.add_handler(CommandHandler("start",start)); app.add_handler(CommandHandler("help",help_cmd)); app.add_handler(CommandHandler("chat",chat_cmd)); app.add_handler(CommandHandler("task",task_cmd)); app.add_handler(CommandHandler("tasks",tasks_cmd)); app.add_handler(CommandHandler("note",note_cmd)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text_msg))
    app.run_polling(drop_pending_updates=False)
if __name__=="__main__": main()
