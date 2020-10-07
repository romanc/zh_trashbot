# -*- coding: utf-8 -*-

import configparser
import json
import logging
import re
import urllib.request

from datetime import datetime, date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler, PicklePersistence, Updater

# configure logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


ZIPCODE, CONFUSED = range(2)


def start(update, context):
    """Handles /start command"""
    update.message.reply_text(
        "Waste collection in Zurich occurs on different days depending on you zip code.\n\nPlease share your 4 digit zip code with me.")

    return ZIPCODE


def zip_handler(update, context):
    """Tries to filter a zip code from the reply text"""
    zips = re.findall(r"\b\d{4}\b", update.message.text)

    if len(zips) == 1:
        zip_code = zips[0]
        context.user_data['zip_code'] = zip_code
        update.message.reply_text(
            "Thank you! Setting your zip code to %s" % zip_code)
        return ConversationHandler.END

    update.message.reply_text(
        "I'm sorry, I didn't get that \U0001F61E\nPlease either share your 4 digit zip code or write /cancel to abort the conversation.")
    return ZIPCODE


def help(update, context):
    """Handles /help command"""
    update.message.reply_text("You are confused? Me too! Sorry \U0001F615")


def upcomming(update, context):
    if 'zip_code' not in context.user_data:
        update.message.reply_text(
            "Hang on!\n\nI need to know where you live before I can look up the calendar for you. Please use /start first to configure this.")
        return

    keyboard = [[InlineKeyboardButton("\U0001F4F0", callback_data='paper'),
                 InlineKeyboardButton("\U0001F4E6", callback_data='cardboard'),
                 InlineKeyboardButton("\U0001F455", callback_data='textile')],

                [InlineKeyboardButton("Cargo \U0001F68B",
                                      callback_data='cargotram'),
                 InlineKeyboardButton("E - \U0001F68B",
                                      callback_data='etram')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'What do you want to throw away?:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query

    query.answer()

    name = {
        "paper": "paper collection \U0001F4F0",
        "cardboard": "cardboard collection \U0001F4E6",
        "textile": "textile collection \U0001F455",
        "cargotram": "cargo tram \U0001F68B",
        "etram": "E-tram \U0001F68B"
    }

    baseurl = "http://openerz.metaodi.ch/api/calendar"
    openerz = "%s/%s.json?zip=%s&start=%s&offset=0&limit=1" % (
        baseurl, query.data, context.user_data['zip_code'], datetime.today().strftime('%Y-%m-%d'))

    with urllib.request.urlopen(openerz) as url:
        data = json.loads(url.read().decode())
        if data['_metadata']['total_count'] == 0:
            query.edit_message_text("I couldn't find any %s in your area \U0001F62D (zip code = %s).\n\nIf you think your zip code is wrong, use /start to configure a new one." % (
                name[query.data], context.user_data['zip_code']))
            return

        next_date = date.fromisoformat(
            data['result'][0]['date']).strftime('%a, %b %d %Y')

    query.edit_message_text(text="Next %s in your area:\n%s" %
                            (name[query.data], next_date))


def echo(update, context):
    """Repeats whatever the user writes"""
    update.message.reply_text(update.message.text)


def cancel(update, context):
    update.message.reply_text("Okay. Gotta go, bye! \U0001F44B")
    return ConversationHandler.END


def settings(update, context):
    zip = context.user_data.get('zip_code', 'undefined')
    update.message.reply_text(
        "I store only very few settings. Currently, I know the following about you:\n\n\t\U00002022 zip code: %s\n\nIf you want to change your zip-code, use /start to configure a new one.\n\nUse /clear to remove all user data mentioned above." % zip)


def clear(update, context):
    context.user_data.clear()
    update.message.reply_text(
        "All user data cleared!\n\nYou will need to user /start again to configure your zip code.")


def trashbot(token):
    """Entry point for trashbot"""
    pickle = PicklePersistence(filename="trashbot_data")
    updater = Updater(token, persistence=pickle, use_context=True)

    myDispatcher = updater.dispatcher

    start_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ZIPCODE: [MessageHandler(Filters.text & ~Filters.command, zip_handler)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    myDispatcher.add_handler(start_conv)
    myDispatcher.add_handler(CommandHandler("help", help))
    myDispatcher.add_handler(CommandHandler("cancel", cancel))
    myDispatcher.add_handler(CommandHandler("settings", settings))
    myDispatcher.add_handler(CommandHandler("clear", clear))

    myDispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo))

    myDispatcher.add_handler(CommandHandler("upcomming", upcomming))
    myDispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    logger.info("Parsing configfile")
    config = configparser.ConfigParser()
    config.read("../config.ini")
    logger.info("Running Züri Trash Bot")
    trashbot(config['api.telegram.org']['token'])
