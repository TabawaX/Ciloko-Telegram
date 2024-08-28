import logging
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from commands import get_command_handlers
from admin import bot_token
from cilok_base import get_handlers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    application = ApplicationBuilder().token(bot_token).build()

   
    for handler in get_command_handlers():
        application.add_handler(handler)

    for handler in get_handlers():
        application.add_handler(handler)

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()