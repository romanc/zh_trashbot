# -*- coding: utf-8 -*-

import configparser
import json
import logging
import urllib.request

from datetime import datetime, date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater

# configure logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    """Handles /start command"""
    update.message.reply_text("Hi & welcome!")


def help(update, context):
    """Handles /help command"""
    update.message.reply_text("You are confused? Me too! Sorry :/")


def upcomming(update, context):
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
        baseurl, query.data, "8006", datetime.today().strftime('%Y-%m-%d'))

    with urllib.request.urlopen(openerz) as url:
        data = json.loads(url.read().decode())
        next_date = date.fromisoformat(
            data['result'][0]['date']).strftime('%a %x')

    query.edit_message_text(text="Next %s in your area: %s" %
                            (name[query.data], next_date))


def echo(update, context):
    """Repeats whatever the user writes"""
    update.message.reply_text(update.message.text)


def trashbot(token):
    """Entry point for trashbot"""
    updater = Updater(token, use_context=True)

    myDispatcher = updater.dispatcher

    myDispatcher.add_handler(CommandHandler("start", start))
    myDispatcher.add_handler(CommandHandler("help", help))

    myDispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo))

    myDispatcher.add_handler(CommandHandler("upcomming", upcomming))
    myDispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print("Parsing configfile")
    config = configparser.ConfigParser()
    config.read("../config.ini")
    print("Running Züri Trash Bot")
    trashbot(config['api.telegram.org']['token'])
