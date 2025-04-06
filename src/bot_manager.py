import os
import logging
from logging.handlers import RotatingFileHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv
from image_processing import ImageProcessor

load_dotenv()

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

# Get environment variables
TOKEN = os.environ['TELE_API_TOKEN']
TEMP_DIR = os.environ['CACHE_DIR']

class BotHandler:
    """Class to handle bot-related tasks."""
    def __init__(self, token: str, temp_dir: str):
        self.token = token
        self.temp_dir = temp_dir
        self.image_processor = ImageProcessor()
        self.user_videos = {}  # Track user videos by chat_id

    async def start(self, update: Update, context: CallbackContext):
        """Handle the /start command."""
        welcome_message = (
            """🌞 Welcome to the Furious 5s Videobooth! 🏖️

Get ready to join the beary best beach party ever! 🐻🏉🎥

Upload your video, and watch as we work some cinematic magic to turn it into a masterpiece! 🎬📸✨ We’re here to make your memories even more awesome! 🍿🎉

⚡️ Ready for some fun? Let’s make your video a beary unforgettable experience!

Oh, and if you're an iPhone user and having trouble downloading your video, don’t worry! Just hit up the /help command and we’ll guide you through it! 🐾🌴"""
        )
        await update.message.reply_text(welcome_message)


    async def help(self, update: Update, context: CallbackContext):
        """Handle the /help command."""
        help_message = (
            """🦝🐻🐼 Need a little help? 🏖️

🌊☀️ If you're having trouble downloading your video on iPhone, don't worry! Follow these simple steps to get your paws on that awesome video we made for you:

1. 📲 Make sure Telegram has full access to your media in your iPhone's settings.
2. 🦁 When you receive your processed video, tap and hold the video until you see a drop-down menu.
3. 🐻 Select "Save Video" to download your masterpiece! 🎥✨
4. 🐨 Once downloaded, you'll find it in your iPhone's gallery. 🏝️

If you're still having trouble, just approach a beary friendly Furious 5s volunteer and we'll lend you a helping paw! 🐾🌴
"""
        )
        await update.message.reply_text(help_message)


    async def handle_video(self, update: Update, context: CallbackContext):
        """Handle video uploads and process them immediately."""
        try:
            # Get the video file
            file = await update.message.video.get_file()
            file_path = os.path.join(self.temp_dir, f"{update.message.chat_id}_{file.file_id}.mp4")
            await file.download_to_drive(file_path)

            # Define output paths for both videos
            output_video_path_1 = os.path.join(self.temp_dir, f"{update.message.chat_id}_output_1.mp4")
            output_video_path_2 = os.path.join(self.temp_dir, f"{update.message.chat_id}_output_2.mp4")
            await update.message.reply_text("Got it! Processing your video 🎥 (this might take a minute or two)...")

            # Process the video and overlay the frame for both portrait and landscape
            self.image_processor.create_stop_motion_video(
                file_path,  # Use the uploaded video
                output_video_path_1,
                output_video_path_2,
                duration_seconds=4,  # Adjust the duration here
                fps=20
            )

            # Send the processed videos to the user
            with open(output_video_path_1, 'rb') as video_file_1:
                await update.message.reply_document(video_file_1, caption="🎞️ Option 1 🎥")

            with open(output_video_path_2, 'rb') as video_file_2:
                await update.message.reply_document(video_file_2, caption="🎞️ Option 2 🎥")

            await update.message.reply_text("Here you go! Hope you like it beary much! Come back soon! 🎬")

            # Clean up temporary files after processing
            self.clean_up_files(update.message.chat_id)

        except Exception as e:
            logging.error(f"Error handling video: {e}")
            await update.message.reply_text(f"Sorry, something went wrong while processing the video. {str(e)} Please try again.")

    def clean_up_files(self, chat_id):
        """Delete all temporary files in TEMP_DIR after processing."""
        try:
            # List all files in the temporary directory
            for file_name in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file_name)

                # Check if it's a file (not a directory)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.debug(f"Deleted file: {file_path}")

            # Clear the user's list of videos
            if chat_id in self.user_videos:
                self.user_videos[chat_id].clear()

        except Exception as e:
            logging.error(f"Error cleaning up files in {self.temp_dir} for user {chat_id}: {e}")
