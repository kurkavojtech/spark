# S.P.A.R.K: System for Personal Archives, Reminders, and Knowledge
# Entry point for the personal AI assistant

import os
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram import Update
import dotenv
from src.agent_team import spark_team

dotenv.load_dotenv()

TG_BOT_ID = os.getenv("TG_BOT_ID")

# --- TELEGRAM HANDLER UPDATE ---
async def telegram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message.text
    response = await spark_team.arun(message, user_id=user_id)
    await update.message.reply_text(response.content if hasattr(response, 'content') else str(response))

def main():
    print("Starting S.P.A.R.K Telegram bot...")
    application = Application.builder().token(TG_BOT_ID).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_handler))
    application.run_polling()

if __name__ == "__main__":
    main()
