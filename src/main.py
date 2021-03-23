from controller.controller import Controller
from controller.contexto import Contexto
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from dotenv import load_dotenv
import os 

load_dotenv()

PORT = int (os.environ.get ('PORT', os.getenv('PORTA')))

TOKEN = os.getenv('TOKEN')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

# from g1_spider import Buscador
# from spider import G1Spider, Control as con
def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    controller.get_contexto().set_bot(context.bot)
    controller.get_contexto().set_user(update.message.from_user)

    controller.add_update(update)
    controller.define_texto_analise(update.message.text)
    controller.process()
    

def main():
    global controller

    controller = Controller()

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # # Start the Bot
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=TOKEN)
    # updater.bot.setWebhook('https://mighty-basin-74579.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
    