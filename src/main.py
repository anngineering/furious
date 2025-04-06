import os
import logging
from PIL import Image, ImageDraw
import imageio
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from image_processing import ImageProcessor
from bot_manager import BotHandler

import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotating file handler
log_handler = RotatingFileHandler('../logs/bot.log', maxBytes=5*1024*1024, backupCount=3)
log_handler.setLevel(logging.INFO)  # Adjust level as needed

# Create formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

# Get the root logger and add the handler to it
logger = logging.getLogger()
logger.addHandler(log_handler)

# Example logging statements
logger.info("Bot is starting...")

load_dotenv()

# Get environment variables
TOKEN = os.environ['TELE_API_TOKEN']
TEMP_DIR = os.environ['CACHE_DIR']


class MainApp:
    """Class to run the bot."""
    
    def __init__(self, token: str, temp_dir: str):
        self.bot_handler = BotHandler(token, temp_dir)

    def run(self):
        """Set up and run the bot."""
        bot_handler = BotHandler(TOKEN, TEMP_DIR)

        # Create the application with the bot token
        application = Application.builder().token(TOKEN).build()

        # Command handlers
        application.add_handler(CommandHandler("start", bot_handler.start))
        application.add_handler(CommandHandler("help", bot_handler.help))

        # Image handler to process incoming photos
        application.add_handler(MessageHandler(filters.VIDEO, bot_handler.handle_video))

        # Start polling to receive updates
        application.run_polling()


if __name__ == "__main__":
    app = MainApp(TOKEN, TEMP_DIR)
    app.run()
