"""Telegram bot logic."""

import configparser
import logging
import random
import time

from itertools import islice

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import filters, ApplicationBuilder, ContextTypes
from telegram.ext import CommandHandler, MessageHandler

from data import read_from_file
from user import VAULI, EVGSOL, PONIK, UNHEILIG, KAIMIRA, HARPY

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

    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I need one (and only one) number argument for this command.")
        return
    try:
        probability = int(context.args[0], 10)
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I need one (and only one) number argument for this command.")
        return

    data = read_from_file(update.effective_chat.id)
    data.chain.probability = probability
    data.write_to_file(update.effective_chat.id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Replies probability updated successfully.")

async def get_probability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/get_probability handler."""

    data = read_from_file(update.effective_chat.id)
    prob = data.chain.probability
    reply = f"Replies in this chat appear approximately once every {prob} messages."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

async def add_dungeon_subscriber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/dungeon_reg handler."""

    data = read_from_file(update.effective_chat.id)
    data.add_dungeon_subscriber(update.effective_user.id)
    data.write_to_file(update.effective_chat.id)

    answer = "Noted."
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer, reply_to_message_id=update.message.id)

async def remove_dungeon_subscriber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/dungeon_unreg handler."""

    data = read_from_file(update.effective_chat.id)
    data.remove_dungeon_subscriber(update.effective_user.id)
    data.write_to_file(update.effective_chat.id)

    answer = "Noted."
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer, reply_to_message_id=update.message.id)

async def add_tmp_dungeon_subscriber(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/dungeon_reg_once handler."""

    data = read_from_file(update.effective_chat.id)
    data.remove_dungeon_subscriber(update.effective_user.id)
    data.add_tmp_dungeon_subscriber(update.effective_user.id)
    data.write_to_file(update.effective_chat.id)

    answer = "Noted."
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer, reply_to_message_id=update.message.id)

def split(iterable, size):
    """Split iterable by chunks."""

    iterable = iter(iterable)
    return iter(lambda: tuple(islice(iterable, size)), ())


MAX_MENTIONS_IN_MESSAGE = 4

async def ping_dungeon_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ping all dungeon subscribers."""

    data = read_from_file(update.effective_chat.id)
    user_ids = list(set(data.dungeon_subscribers + data.tmp_dungeon_subscribers))
    mentions = []

    if user_ids:
        for user_id in user_ids:
            error = None
            for _ in range(5):
                try:
                    chat_member = await context.bot.get_chat_member(
                        chat_id=update.effective_chat.id, user_id=user_id)
                    mentions.append(chat_member.user.mention_html())
                    break
                except BadRequest as caught_error:
                    error = caught_error
            else:
                logging.error("Failed to get info about %s: %s", user_id, error)

        chunks = split(mentions, MAX_MENTIONS_IN_MESSAGE)
        for chunk in chunks:
            answer = "\n".join(chunk)
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=answer, parse_mode=ParseMode.HTML)

        data.tmp_dungeon_subscribers = []
        data.write_to_file(update.effective_chat.id)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="No subscribers now.")

def is_ponik(update: Update):
    """Checks if message author is Ponik."""

    return update.effective_user.id == PONIK.user_id

async def good_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Good morning messages handler."""

    answer = "Ты не Поник. >_>"
    if is_ponik(update):
        answer = "Утречка, Поник!"

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer, reply_to_message_id=update.message.id)

async def good_night(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Good night sticker handler."""

    answer = "Good night, sweet prince!"
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=answer, reply_to_message_id=update.message.id)

async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Countdown messages handler."""

    countdown_phrases = ((
        "Ten (Ground control)",
        "Nine (to Major Tom)",
        "Eight, seven, six (Commencing)",
        "Five (countdown, engines on)",
        "Four, three, two (Check ignition)",
        "One (and may God's love)",
        "Lift off (be with you)"
    ), (
        "Ten (kiss me on the lips)",
        "Nine (run your fingers through my hair)",
        "Eight (touch me... slowly)",
        "Hold it! Let's go straight...",
        "To number one!"
    ))
    for phrase in random.choice(countdown_phrases):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=phrase)
        time.sleep(1)

PHRASES = [
    """Excalibur! Excalibur!
From the United King!
I'm looking for Heaven!
I'm going to California!
Excalibur!
Excalibur!""",
    "Дурачье!",
    "Моя история началась в 12-том веке..."
]

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text messages handler."""

    if update.message is None or update.message.text is None:
        return
    if len(update.message.text) == 0:
        return

    print(update.message["from"])

    if "".join(filter(lambda x: x.isalpha(), update.message.text.lower())) in (
            "утречкачятик",
            "утречкачатик"
    ):

        await good_morning(update, context)
        return

    data = read_from_file(update.effective_chat.id)
    data.chain.add_message(update.message.text)
    data.write_to_file(update.effective_chat.id)

    named = ("excalibur" in update.message.text.lower()
             or "экскалибур" in update.message.text.lower())

    if named and (
            "считай" in update.message.text.lower() or
            "щетуй" in update.message.text.lower() or
            "щетaй" in update.message.text.lower() or
            "щитуй" in update.message.text.lower() or
            "щитуемо" in update.message.text.lower()
    ):
        await countdown(update, context)
        return

    force = named
    if update.message.reply_to_message is not None:
        if update.message.reply_to_message["from"]["id"] == context.bot.id:
            force = True

    if force and (
            "угнетайся" in update.message.text.lower() or
            "калькулятор" in update.message.text.lower()
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Угнетаюсь. :(",
            reply_to_message_id=update.message.id)
        return

    answer = data.chain.gen_answer_with_probability(update.message.text, force=force)
    if answer is None:
        if not force:
            return
        answer = "I don't know what to say here;"
        answer += " need some more time to learn things in this chat."

    if named is True and random.randrange(2):
        answer = random.choice(PHRASES)

    if answer is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=answer, reply_to_message_id=update.message.id)


OWNERS = {
    "Elisey": PONIK,
    "lmp_vk": UNHEILIG,
    "spf6df055576a9675c9d1a22fe6ce826a3_by_stckrRobot": KAIMIRA,
    "spe2bdb80721de76d8feea189dd9d7412f_by_stckrRobot": KAIMIRA,
    "BabyYoda": VAULI,
    "AlcoLan": HARPY,
}

GOOD_NIGHT_STICKER = "AgADPAADR_sJDA"
STICKERS_MAP = {
    GOOD_NIGHT_STICKER: good_night
}

async def sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Text messages handler."""

    if update.message is None:
        return
    if update.message.sticker is None:
        return

    if update.message.sticker.set_name in OWNERS:
        if update.message["from"].id != OWNERS[update.message.sticker.set_name].user_id:
            name = OWNERS[update.message.sticker.set_name].name
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"Ты не {name}. >_>",
                reply_to_message_id=update.message.id)
            return

    if update.message.sticker.file_unique_id in STICKERS_MAP:
        await STICKERS_MAP[update.message.sticker.file_unique_id](update, context)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")

    application = ApplicationBuilder().token(config["Credentials"]["token"]).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message)
    sticker_handler = MessageHandler(filters.Sticker.ALL, sticker)
    ping_handler = CommandHandler('ping', ping)
    set_probability_handler = CommandHandler('set_probability', set_probability)
    get_probability_handler = CommandHandler('get_probability', get_probability)
    dungeon_reg_handler = CommandHandler('dungeon_reg', add_dungeon_subscriber)
    dungeon_unreg_handler = CommandHandler('dungeon_unreg', remove_dungeon_subscriber)
    dungeon_reg_once_handler = CommandHandler('dungeon_reg_once', add_tmp_dungeon_subscriber)
    dungeon_ping_handler = CommandHandler('dungeon_ping', ping_dungeon_subscribers)
    countdown_handler = CommandHandler('countdown', countdown)

    application.add_handler(start_handler)
    application.add_handler(ping_handler)
    application.add_handler(message_handler)
    application.add_handler(sticker_handler)
    application.add_handler(set_probability_handler)
    application.add_handler(get_probability_handler)
    application.add_handler(dungeon_reg_handler)
    application.add_handler(dungeon_unreg_handler)
    application.add_handler(dungeon_reg_once_handler)
    application.add_handler(dungeon_ping_handler)
    application.add_handler(countdown_handler)

    application.run_polling()
