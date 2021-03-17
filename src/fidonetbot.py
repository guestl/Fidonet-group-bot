# Python-telegram-bot libraries
import telegram
from telegram.ext import Updater, MessageHandler, Filters

# Logging and requests libraries
import logging
from logging.handlers import RotatingFileHandler

# Importing token from config file
import config
from fidonetbot_db_helper import fidonetbot_db_helper


database = fidonetbot_db_helper()

# Logging module for debugging
log_format = '%(asctime)s %(filename)-12s %(funcName)s %(lineno)d %(message)s'
logging.basicConfig(handlers=[RotatingFileHandler('fidonet_bot.log',
                                                  maxBytes=500000,
                                                  backupCount=5)],
                    format=log_format,
                    level=config.LOGGER_LEVEL)

logger = logging.getLogger(__name__)  # this gets the root logger
logger.setLevel(config.LOGGER_LEVEL)


# /18, gfg /18 gdsgf
def get_fido_addr_from_text(text_with_possible_addr):
    ind = text_with_possible_addr.find('/')
    end_ind = text_with_possible_addr.find(' ', ind + 1)

    if end_ind == -1:
        end_ind = len(text_with_possible_addr)

    if text_with_possible_addr[ind:end_ind] == '':
        new_str = 'NA'
        {'addr': new_str, 'start': -1}

    if text_with_possible_addr[ind + 1:end_ind].isnumeric():
        new_str = text_with_possible_addr[ind:end_ind]
        {'addr': new_str, 'start': ind}

    new_str = '/'
    for single_char in text_with_possible_addr[ind + 1:end_ind]:
        if single_char.isnumeric() or '.' in single_char:
            new_str += single_char
        else:
            new_str = 'NA'
            return {'addr': new_str, 'start': -1}

    return {'addr': new_str, 'start': ind}


def parse_text_for_fidonet_address(update, context):
    # chat_id = update.message.chat_id
    if update.message.from_user is None:
        return

    if update.message.from_user.id:
        user_id = update.message.from_user.id
    if update.message.from_user.first_name:
        user_names = update.message.from_user.first_name
    if update.message.from_user.last_name:
        user_names += ' ' + update.message.from_user.last_name
    username = update.message.from_user.username
    # message_id = update.message.message_id

    if update.message.text is None:
        return

    database.update_by_somename(user_id, user_names, username)

    if '/' in update.message.text:
        addr_dict = get_fido_addr_from_text(update.message.text)
        logger.info(addr_dict)
        if addr_dict['start'] != -1:
            result = database.get_fidodata_by_text(addr_dict['addr'])
        else:
            return
        logger.info(result)

        new_str = update.message.text
        new_str = new_str.replace(addr_dict['addr'], result)

        update.message.reply_text(result)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.error('Update caused error "%s"', context.error)


def main():
    bot = telegram.Bot(token=config.token)

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=config.token, use_context=True)

    logger.info("Authorized on account %s. "
                "version is %s" % (bot.username, config.version))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text | Filters.command,
                                          parse_text_for_fidonet_address))

    # log all errors
    # dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
