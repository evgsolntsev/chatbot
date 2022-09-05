"""Telegram bot logic."""

import configparser
import logging

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

from markov import write_to_file, read_from_file, Chain

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start handler."""

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hi! I'm a chatbot. I will type something here from time to time.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ping handler."""

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Pong.")

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text messages handler."""

    chain = read_from_file(update.effective_chat.id)
    chain.add_message(update.message.text)
    write_to_file(chain, update.effective_chat.id)

    answer = chain.gen_answer(update.message.text)
    if answer is None:
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

if __name__ == '__main__':
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("settings.ini")

    application = ApplicationBuilder().token(config["Credentials"]["token"]).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message)
    ping_handler = CommandHandler('ping', ping)

    application.add_handler(start_handler)
    application.add_handler(ping_handler)
    application.add_handler(message_handler)

    application.run_polling()
