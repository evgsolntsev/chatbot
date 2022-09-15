"""Telegram bot logic."""

import configparser
import logging

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler

from markov import write_to_file, read_from_file

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

async def set_probability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/set_probability handler."""

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Pong.")

async def get_probability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/get_probability handler."""

    chain = read_from_file(update.effective_chat.id)
    reply = f"Replies in this chat appear approximately once every {chain.probability} messages."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text messages handler."""

    if update.message is None:
        return
    if update.message.text is None:
        return
    if len(update.message.text) == 0:
        return

    chain = read_from_file(update.effective_chat.id)
    chain.add_message(update.message.text)
    write_to_file(chain, update.effective_chat.id)

    force = ("excalibur" in update.message.text.lower()
             or "экскалибур" in update.message.text.lower())
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message["from"]["id"] == context.bot.id:
            force = True

    answer = chain.gen_answer_with_probability(update.message.text, force=force)
    if answer is None:
        if not force:
            return
        answer = "I don't know what to say here;"
        answer += " need some more time to learn things in this chat."

    if answer is None:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer, reply_to_message_id=update.message.id)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")

    application = ApplicationBuilder().token(config["Credentials"]["token"]).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message)
    ping_handler = CommandHandler('ping', ping)
    set_probability_handler = CommandHandler('set_probability', set_probability)
    get_probability_handler = CommandHandler('get_probability', get_probability)

    application.add_handler(start_handler)
    application.add_handler(ping_handler)
    application.add_handler(message_handler)
    application.add_handler(set_probability_handler)
    application.add_handler(get_probability_handler)

    application.run_polling()
