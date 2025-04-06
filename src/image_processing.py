import cv2
import os
from dotenv import load_dotenv
import numpy as np
import logging
from PIL import Image
import imageio

load_dotenv()

TEMP_DIR = os.environ['CACHE_DIR']
PORTRAIT_OVERLAY_PATH_1 = os.environ['PORTRAIT_OVERLAY_FRAME_1_DIR']
PORTRAIT_OVERLAY_PATH_2 = os.environ['PORTRAIT_OVERLAY_FRAME_2_DIR']
LANDSCAPE_OVERLAY_PATH_1 = os.environ['LANDSCAPE_OVERLAY_FRAME_1_DIR']
LANDSCAPE_OVERLAY_PATH_2 = os.environ['LANDSCAPE_OVERLAY_FRAME_2_DIR']

class ImageProcessor:
    """Class to handle all image processing tasks."""
    
    def __init__(self, portrait_overlay_path_1=PORTRAIT_OVERLAY_PATH_1, 
    portrait_overlay_path_2=PORTRAIT_OVERLAY_PATH_2, 
    landscape_overlay_path_1=LANDSCAPE_OVERLAY_PATH_1, 
    landscape_overlay_path_2=LANDSCAPE_OVERLAY_PATH_2, 
    temp_dir=TEMP_DIR):
        self.portrait_overlay_path_1 = portrait_overlay_path_1
        self.portrait_overlay_path_2 = portrait_overlay_path_2
        self.landscape_overlay_path_1 = landscape_overlay_path_1
        self.landscape_overlay_path_2 = landscape_overlay_path_2
        self.temp_dir = temp_dir

    def overlay_frame(self, image: Image):
        """Overlay a PNG frame based on image orientation (portrait or landscape)."""
        try:
            # Get the size of the uploaded image
            image_width, image_height = image.size

            # Check if the image is in portrait mode (height > width)
            if image_height > image_width:
                # Portrait mode: use portrait overlay and resize it
                frame_1 = Image.open(self.portrait_overlay_path_1).convert("RGBA")
                frame_1_resized = frame_1.resize((image_width, image_height), Image.Resampling.LANCZOS)
                frame_2 = Image.open(self.portrait_overlay_path_2).convert("RGBA")
                frame_2_resized = frame_2.resize((image_width, image_height), Image.Resampling.LANCZOS)

            else:
                # Landscape mode: use landscape overlay and resize it
                frame_1 = Image.open(self.landscape_overlay_path_1).convert("RGBA")
                frame_1_resized = frame_1.resize((image_width, image_height), Image.Resampling.LANCZOS)
                frame_2 = Image.open(self.landscape_overlay_path_2).convert("RGBA")
                frame_2_resized = frame_2.resize((image_width, image_height), Image.Resampling.LANCZOS)
            
            # Use alpha channel as mask for transparency
            alpha_mask_1 = frame_1_resized.split()[3]
            alpha_mask_2 = frame_2_resized.split()[3]
            
            # Paste the resized frame onto the image for both options
            image_pasted_1 = image.copy()
            image_pasted_2 = image.copy()
            
            image_pasted_1.paste(frame_1_resized, (0, 0), alpha_mask_1)
            image_pasted_2.paste(frame_2_resized, (0, 0), alpha_mask_2)

            return image_pasted_1, image_pasted_2  # Return both frames
        except Exception as e:
            logging.error(f"Error overlaying frame: {e}")
            raise ValueError(f"Error overlaying frame: {e}")


    def create_video(self, video_path, output_path_1, output_path_2, duration_seconds=4, fps=15):
        """Process the video, overlay a frame on each frame, and output two distinct MP4 videos."""
        try:
            # Open the video file
            cap = cv2.VideoCapture(video_path)

            # Get the original video properties
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            total_duration_seconds = total_frames / original_fps

            # Calculate the frame count for the specified duration
            frames_to_process = int(min(duration_seconds, total_duration_seconds) * original_fps)

            # Create two VideoWriters to save the output videos
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Video writer for frame_1
            out_1 = cv2.VideoWriter(output_path_1, fourcc, fps, (width, height))
            # Video writer for frame_2
            out_2 = cv2.VideoWriter(output_path_2, fourcc, fps, (width, height))

            for frame_idx in range(frames_to_process):
                ret, frame = cap.read()
                if not ret:
                    logging.warning("Failed to read frame from video.")
                    break

                # Convert frame to PIL for overlay processing
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # Overlay the frame onto the image and get both frame variations
                processed_image_1, processed_image_2 = self.overlay_frame(pil_image)

                # Convert the processed image to OpenCV format for both frames
                processed_frame_1 = cv2.cvtColor(np.array(processed_image_1), cv2.COLOR_RGB2BGR)
                processed_frame_2 = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_RGB2BGR)

                # Write the frames to their respective output videos
                out_1.write(processed_frame_1)
                out_2.write(processed_frame_2)

            # Release video capture and writer
            cap.release()
            out_1.release()
            out_2.release()

            logging.info(f"Processed videos saved to {output_path_1} and {output_path_2}")

        except Exception as e:
            logging.error(f"Error processing video: {e}")
            raise ValueError(f"Error processing video: {e}")


    def create_stop_motion_video(self, video_path, output_path_1, output_path_2, duration_seconds=4, fps=24, frame_interval_ms=100):
        """Create stop-motion like videos by sampling frames every X milliseconds and overlaying two different frames."""
        try:
            # Open the video file
            cap = cv2.VideoCapture(video_path)

            # Get the original video properties
            original_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            total_duration_seconds = total_frames / original_fps

            # Calculate the frame count for the specified duration
            frames_to_process = int(min(duration_seconds, total_duration_seconds) * original_fps)

            # Create two VideoWriters to save the output videos
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Video writer for frame_1
            out_1 = cv2.VideoWriter(output_path_1, fourcc, fps, (width, height))
            # Video writer for frame_2
            out_2 = cv2.VideoWriter(output_path_2, fourcc, fps, (width, height))

            # Frame interval based on the ms input (convert to frame count)
            frame_interval = int(original_fps * frame_interval_ms / 1000)  # ms to frame count
            
            for frame_idx in range(0, frames_to_process, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)  # Set to the correct frame
                
                ret, frame = cap.read()
                if not ret:
                    logging.warning("Failed to read frame from video.")
                    break

                # Convert frame to PIL for overlay processing
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # Overlay the frame onto the image, and get both frames
                processed_image_1, processed_image_2 = self.overlay_frame(pil_image)

                # Convert the processed images to OpenCV format for both frames
                processed_frame_1 = cv2.cvtColor(np.array(processed_image_1), cv2.COLOR_RGB2BGR)
                processed_frame_2 = cv2.cvtColor(np.array(processed_image_2), cv2.COLOR_RGB2BGR)

                # Write the frames to their respective output videos
                out_1.write(processed_frame_1)
                out_2.write(processed_frame_2)

            # Release video capture and writer
            cap.release()
            out_1.release()
            out_2.release()

            logging.info(f"Processed stop-motion videos saved to {output_path_1} and {output_path_2}")

        except Exception as e:
            logging.error(f"Error processing video: {e}")
            raise ValueError(f"Error processing video: {e}")
