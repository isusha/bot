import os
from telegram.ext import Updater, CommandHandler

TOKEN = os.getenv(8296435065:AAFCDjuerTbm8P6xRJd6-RD63H_Gzc29FQA)

def start(update, context):
    update.message.reply_text("Привет! Я живой бот 🚀")

updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler("start", start))

updater.start_polling()
updater.idle()
