# -*- coding: utf-8 -*-

import logging
import configparser

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# configure logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    """Handles /start command"""
    update.message.reply_text("Hi & welcome!")

def help(update, context):
    """Handles /help command"""
    update.message.reply_text("You are confused? Me too! Sorry :/")

def echo(update, context):
    """Repeats whatever the user writes"""
    update.message.reply_text(update.message.text)

def echobot(token):
    """Entry point for echo bot"""
    updater = Updater(token, use_context=True)

    myDispatcher = updater.dispatcher

    myDispatcher.add_handler(CommandHandler("start", start))
    myDispatcher.add_handler(CommandHandler("help", help))

    myDispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print("Parsing configfile")
    config = configparser.ConfigParser()
    config.read("../config.ini")
    print("Running echo_bot")
    echobot(config['api.telegram.org']['token'])

