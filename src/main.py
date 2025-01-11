import os
import logging
from PIL import Image, ImageDraw
import imageio
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

load_dotenv()

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Get environment variables
TOKEN = os.environ['TELE_API_TOKEN']
TEMP_DIR = os.environ['CACHE_DIR']
OVERLAY_PATH = os.environ['OVERLAY_FRAME_DIR']

# Function to overlay a frame onto an image
def overlay_frame(image_path, frame_path=OVERLAY_PATH, position=(0, 0)):
    """Overlay a PNG frame onto an image."""
    try:
        # Open the base image (the image to which the frame will be applied)
        img = Image.open(image_path).convert("RGBA")  # Ensure image is in RGBA mode (with transparency)
        
        # Open the frame image (with transparent background)
        frame = Image.open(frame_path).convert("RGBA")  # Ensure frame is in RGBA mode

        # Resize the frame to match the base image size
        frame = frame.resize(img.size, Image.Resampling.LANCZOS)  # Updated resizing method

        # Paste the frame onto the base image using the alpha channel as a mask for transparency
        img.paste(frame, position, frame)  # `position` is where the frame will be placed on the image
        
        return img
    except Exception as e:
        logging.error(f"Error overlaying frame: {e}")
        raise ValueError(f"Error overlaying frame: {e}")

# Function to create a GIF from images
def create_gif(image_paths, gif_path, duration=0.5):
    """Create a GIF from the given image paths."""
    images = [imageio.imread(image_path) for image_path in image_paths]
    imageio.mimsave(gif_path, images, duration=duration)

# Start command to welcome the user
async def start(update: Update, context: CallbackContext):
    welcome_message = (
        "🌞 Welcome to the Furious 5s Photobooth! 🏖️\n\n"
        "Upload up to 4 photos and I’ll turn them into a fun GIF for you and your pack! 📸🐨🐼🐻🐻‍❄️📸\n"
        "Get ready to have a beary jolly time 🐻🏉.\n\n"
    )
    await update.message.reply_text(welcome_message)

# Function to handle image uploads
async def handle_image(update: Update, context: CallbackContext):
    try:
        # Await the get_file() to get the actual file object
        file = await update.message.photo[-1].get_file()  # Get the highest resolution photo
        
        # Define the file path where the photo will be saved
        file_path = os.path.join(TEMP_DIR, f"{update.message.chat_id}_{file.file_id}.jpg")
        
        # Download the file to the specified file path
        await file.download(file_path)  # Await the download to ensure completion
        
        # Apply the frame to the image
        framed_image = overlay_frame(file_path)
        framed_image_path = f"framed_{file_path}"
        framed_image.save(framed_image_path)

        # Ensure 'framed_images' is initialized in context.bot_data
        if 'framed_images' not in context.bot_data:
            context.bot_data['framed_images'] = []
        
        # Add the framed image to the list
        context.bot_data['framed_images'].append(framed_image_path)

        # If 4 images have been received, create a GIF
        if len(context.bot_data['framed_images']) == 4:
            gif_path = os.path.join(TEMP_DIR, "output.gif")
            create_gif(context.bot_data['framed_images'], gif_path)

            # Send the GIF to the user
            with open(gif_path, 'rb') as gif_file:
                await update.message.reply_document(gif_file)

            # Clean up files after GIF is sent
            clean_up_files()
            context.bot_data['framed_images'] = []

        else:
            await update.message.reply_text("Got it! Send me more images or type /start to restart.")

    except Exception as e:
        logging.error(f"Error handling image: {e}")
        await update.message.reply_text("Sorry, something went wrong. Please try again.")

# Function to clean up temporary files
def clean_up_files():
    """Delete temporary images after processing.""" 
    try:
        for file_name in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        logging.error(f"Error cleaning up files: {e}")

# Main function to set up the bot
def main():
    """Start the bot."""
    # Make sure the temp directory exists
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # Set up the Application (new in version 20+)
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))  # Updated with lowercase `filters`

    # Start the bot (do not wrap in asyncio.run())
    application.run_polling()

if __name__ == "__main__":
    main()
