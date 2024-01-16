# -*- coding: utf-8 -*-

import configparser
import json
import logging
import re
import urllib.request

from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler,\
    ConversationHandler, Filters, MessageHandler, PicklePersistence, Updater

# configure logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# emojis
E_blush = "\U0001F60A"
E_broom = "\U0001F9F9"
E_calendar = "\U0001F4C5"
E_cardboard = "\U0001F4E6"
E_cry = "\U0001F62D"
E_disappointed = "\U0001F61E"
E_gear = "\U00002699"
E_grin = "\U0001F604"
E_paper = "\U0001F4F0"
E_tada = "\U0001F389"
E_textile = "\U0001F455"
E_tram = "\U0001F68B"
E_unsure = "\U0001F615"
E_wave = "\U0001F44B"

CHOOSE, HANDLE_LIMIT, ZIPCODE = range(3)
CURRENT_VERSION = "1.1.0"

WhatsNew = {
    "1.2.0":
        ["Use `/next %s` as a shortcut to query paper collections directly" % E_paper,
        "Deprecated textile %s collection dates" % E_textile,
        "Minor code cleanups"],
    "1.1.0":
        ["Use /configure %s to set a query limit and see more the one collection date" % E_gear,
         "What's new messages %s" % E_grin,
         "Various text improvements",
         "Some code cleanup"]}


def newerVersionExists(userVersion):
    (major, minor, patch) = userVersion.split(".")
    (cMajor, cMinor, cPatch) = CURRENT_VERSION.split(".")
    return major < cMajor or (major == cMajor and (
        minor < cMinor or (minor == cMinor and patch < cPatch)))


def setDefaultUserData(context, key, value):
    if key not in context.user_data:
        context.user_data[key] = value


def whatsNewMessage(context):
    ctx = context.job.context
    context.bot.send_message(ctx["chat_id"], text=ctx["text"])


def startCommand(update, context):
    # setting default user values
    setDefaultUserData(context, "queryLimit", "1")
    setDefaultUserData(context, "version", CURRENT_VERSION)

    reply = "Waste collection in Zurich occurs on different days depending "\
        "on you zip code.\n\n"\
        "Please share your 4 digit zip code with me."
    update.message.reply_text(reply)

    return ZIPCODE


def zipHandler(update, context):
    """Tries to filter a zip code from the reply text"""
    zips = re.findall(r"\b\d{4}\b", update.message.text)

    if len(zips) == 1:
        zip_code = zips[0]
        context.user_data['zip_code'] = zip_code
        msg = "Thank you! Setting your zip code to %s.\n\n"\
            "Now try /next to check for waste collection dates." % zip_code
        update.message.reply_text(msg)
        return ConversationHandler.END

    reply = "I'm sorry, I didn't get that %s\nPlease either share "\
        "your 4 digit zip code or write /cancel to abort the "\
        "conversation." % E_disappointed
    update.message.reply_text(reply)
    return ZIPCODE


def helpCommand(update, context):
    """Handles /help command"""
    update.message.reply_text("Are you confused? Me too! Sorry %s" % E_unsure)


def nextCommand(update, context):
    if 'zip_code' not in context.user_data:
        reply = "Hang on!\n\n"\
            "I need to know where you live before I can look up the "\
            "calendar %s for you. Please use /start to configure your zip "\
            "code." % E_calendar
        update.message.reply_text(reply)
        return

    paper = len(re.findall(r'[' + E_paper + ']', update.message.text))
    if paper > 0:
        nextDates = queryCollectionAPI("paper", context.user_data)
        update.message.reply_text(nextDates)
        return
    cardboard = len(re.findall(r'[' + E_cardboard + ']', update.message.text))
    if cardboard > 0:
        nextDates = queryCollectionAPI("cardboard", context.user_data)
        update.message.reply_text(nextDates)
        return
    textile = len(re.findall(r'[' + E_textile + ']', update.message.text))
    if textile > 0:
        nextDates = queryCollectionAPI("textile", context.user_data)
        update.message.reply_text(nextDates)
        return

    keyboard = [[InlineKeyboardButton(E_paper, callback_data='paper'),
                 InlineKeyboardButton(E_cardboard, callback_data='cardboard'),
                 InlineKeyboardButton(E_textile, callback_data='textile')],

                [InlineKeyboardButton("Cargo %s" % E_tram,
                                      callback_data='cargotram'),
                 InlineKeyboardButton("E - %s" % E_tram,
                                      callback_data='etram')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'What do you want to throw away?', reply_markup=reply_markup)


def queryCollectionAPI(choice, user_data):
    name = {
        "paper": "paper collection %s" % E_paper,
        "cardboard": "cardboard collection %s" % E_cardboard,
        "textile": "textile collection %s" % E_textile,
        "cargotram": "cargo tram %s" % E_tram,
        "etram": "E-tram %s" % E_tram
    }

    if choice == "textile":
        textileException = "The city of Zurich stopped textile collections in "\
            "favor of an increased number of collection stations. You can also "\
            "bring your old cloths to Cargo-Tram %s.\n\n"\
            "For more information (in German) visit erz.ch/textilien." % E_tram
        return textileException

    zip = user_data.get('zip_code', 'undefined')
    limit = user_data.get('queryLimit', "1")
    today = datetime.today().strftime('%Y-%m-%d')

    baseurl = "http://openerz.metaodi.ch/api/calendar.json"
    openerz = "%s?sort=date&types=%s&zip=%s&start=%s" % (baseurl, choice,
                                                        zip, today)
    openerz += "&limit=0" if limit == "none" else "&limit=%s" % limit

    with urllib.request.urlopen(openerz) as url:
        data = json.loads(url.read().decode())
        count = data['_metadata']['total_count']
        if count == 0:
            notFound = "I couldn't find any %s in your area %s "\
                "(zip code = %s).\n\n"\
                "Please note: Especially in December you might see no this "\
                "message if the new year's data isn't publically available "\
                "yet.\n\n"\
                "If you think your zip code is wrong, use /start to "\
                "configure a new one." % (E_cry, name[query.data], zip)
            return notFound

        nextDate = ""
        for result in data['result']:
            date = datetime.strptime(
                result['date'], "%Y-%m-%d").strftime('%a, %b %d %Y')
            nextDate += "\t\U00002022 %s\n" % date
        return "Next %s in your area:\n%s" % (name[choice], nextDate)

    return "Unable to contact openERZ api. Please try again later."


def queryButton(update, context, selected=None):
    query = update.callback_query
    query.answer()

    nextDates = queryCollectionAPI(query.data, context.user_data)
    query.edit_message_text(text=nextDates)


def echo(update, context):
    """Repeats whatever the user writes"""
    update.message.reply_text(update.message.text)


def cancelCommand(update, context):
    update.message.reply_text("Okay. Gotta go, bye! %s" % E_wave)
    return ConversationHandler.END


def configureCommand(update, context):
    opts = [[InlineKeyboardButton("Query limit", callback_data="queryLimit"),
             InlineKeyboardButton("Cancel", callback_data="cancel")]]

    queryLimit = context.user_data.get('queryLimit', "1")
    current = "Your current settings look like this:\n\n"\
        "\t\U00002022 Query limit: %s\n\n"\
        "What do you want to configure? If these settings look just fine, "\
        "use the cancel button." % (queryLimit)

    update.message.reply_text(current, reply_markup=InlineKeyboardMarkup(opts))

    return CHOOSE


def chooseSetting(update, context):
    query = update.callback_query
    query.answer()

    if query.data == "queryLimit":
        keyboard = [[InlineKeyboardButton("1", callback_data="1"),
                     InlineKeyboardButton("2", callback_data="2"),
                     InlineKeyboardButton("5", callback_data="5"),
                     InlineKeyboardButton("all", callback_data="none")]]
        text = "Okay, let's set the query limit. How many collections do you "\
            "want to see per query?"
        query.edit_message_text(text=text,
                                reply_markup=InlineKeyboardMarkup(keyboard))
        return HANDLE_LIMIT
    elif query.data == "cancel":
        query.edit_message_text(
            text="Keeping your settings as is. %s" % E_blush)
        return ConversationHandler.END

    query.edit_message_text(text="I'm sorry, I can't find this setting.")
    return ConversationHandler.END


def handleQueryLimit(update, context):
    query = update.callback_query
    query.answer()

    context.user_data["queryLimit"] = query.data
    reply = ""
    if query.data == "none":
        reply = "Removed query limit - showing all remaining colletion dates "\
            "for each query in the future."
    else:
        reply = "Query limit is set to %s now." % query.data

    query.edit_message_text(reply)
    return ConversationHandler.END


def settingsCommand(update, context):
    zip = context.user_data.get('zip_code', 'undefined')
    limit = context.user_data.get('queryLimit', "1")
    reply = "Züri Trash Bot stores only very few settings.\n"\
        "Currently, the bot knows the following about you:\n\n"\
        "\t\U00002022 zip code: %s\n"\
        "\t\U00002022 query limit: %s\n\n"\
        "If you want to change your zip-code, use /start to configure a new "\
        "one.\n\n"\
        "Use /configure to change any other setting.\n\n"\
        "Use /clear to remove all user data mentioned above." % (zip, limit)
    update.message.reply_text(reply)


def clearCommand(update, context):
    context.user_data.clear()
    reply = "%s All user data cleared!\n\n"\
        "You will need to use /start again to configure your zip "\
        "code." % E_broom
    update.message.reply_text(reply)


def aboutCommand(update, context):
    text = "Züri Trash Bot is an open-source project, see "\
        "https://github.com/romanc/zh_trashbot\n\n"\
        "Züri Trash Bot is made possible by\n"\
        "\t\U00002022 https://github.com/python-telegram-bot\n"\
        "\t\U00002022 http://openerz.metaodi.ch\n\n"\
        "Kudos and keep up the nice work! "\
        "This service is provided 'as is', without warranty of any kind.\n"

    update.message.reply_text(text)


def trashbot(token):
    """Entry point for trashbot"""
    pp = PicklePersistence(filename="trashbot_data")
    updater = Updater(token, persistence=pp, use_context=True)

    startConversation = ConversationHandler(
        entry_points=[CommandHandler('start', startCommand)],

        states={
            ZIPCODE: [MessageHandler(Filters.text & ~Filters.command,
                                     zipHandler)]
        },

        fallbacks=[CommandHandler('cancel', cancelCommand)]
    )
    configureConversation = ConversationHandler(
        entry_points=[CommandHandler("configure", configureCommand)],
        states={
            CHOOSE: [CallbackQueryHandler(chooseSetting)],
            HANDLE_LIMIT: [CallbackQueryHandler(handleQueryLimit)]
        },
        fallbacks=[CommandHandler('cancel', cancelCommand)]
    )

    myDispatcher = updater.dispatcher
    myDispatcher.add_handler(CommandHandler("about", aboutCommand))
    myDispatcher.add_handler(CommandHandler("cancel", cancelCommand))
    myDispatcher.add_handler(CommandHandler("clear", clearCommand))
    myDispatcher.add_handler(CommandHandler("help", helpCommand))
    myDispatcher.add_handler(CommandHandler("next", nextCommand))
    myDispatcher.add_handler(CommandHandler("settings", settingsCommand))

    myDispatcher.add_handler(startConversation)
    myDispatcher.add_handler(configureConversation)
    myDispatcher.add_handler(CallbackQueryHandler(queryButton))

    # echo anything unknown
    myDispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo))

    userData = pp.get_user_data()
    chatData = pp.get_chat_data()

    for item in chatData.items():
        chatId = item[0]
        thisUser = userData[chatId]

        if newerVersionExists(thisUser.get("version", "1.0.2")):
            # we have a newer version
            text = "Here's what's new in version %s %s\n\n" % (
                CURRENT_VERSION, E_tada)
            for note in WhatsNew[CURRENT_VERSION]:
                text = text + ("\t\U00002022 %s\n" % note)

            # send a what's new message
            updater.job_queue.run_once(whatsNewMessage, 2, context={
                "chat_id": chatId, "text": text},
                name="new%s" % str(chatId))

            # then, update current version
            myDispatcher.user_data[chatId]["version"] = CURRENT_VERSION

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    logger.info("Parsing configfile")
    config = configparser.ConfigParser()
    config.read("../config.ini")

    logger.info("Running Züri Trash Bot")
    trashbot(config['api.telegram.org']['token'])
