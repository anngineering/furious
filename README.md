# Furious 5s Videobooth Bot

This repo allows users to upload a video through a Telegram bot, which the first 4 seconds gets cropped for payload optimization, then applies a frame overlay to the video in different styles (portrait and landscape). The bot provides two processed video options that users can download.


### Sample Processed Video
To give you an idea of how the bot processes videos, here's a sample processed video with the overlay applied.

- **[Watch the Sample Video (Portrait Style)](https://drive.google.com/file/d/1pXKAh25CCWLHwvtRopcTTzG1eUovlRu6/view?usp=drivesdk)**


## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Setup Environment Variables](#setup-environment-variables)
4. [Running the Bot Locally](#running-the-bot-locally)
5. [Hosting the Bot on AWS EC2](#hosting-the-bot-on-aws-ec2)
6. [Dependencies](#dependencies)
7. [Contributing](#contributing)

---

## Prerequisites

To run this bot locally, you need:

- Python 3.12 installed.
- A Telegram Bot Token (you can get it from [@BotFather](https://core.telegram.org/bots#botfather)).
- `ffmpeg` installed on your local system for video processing.

Optionally, you could also host this bot on a cloud service such as AWS (instructions included for how to set up an EC2 instance)

## Installation

1. **Clone the repository:**

   ```bash
   git clone git@github.com:anngineering/furious.git
   cd furious
   ```

2. **Create a virtual environment:**

   It’s recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - For **Windows**:
     ```bash
     venv\Scripts\activate
     ```

   - For **Mac/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Setup Environment Variables

1. **Create a `.env` file:**

   Copy the `.env.template` file and rename it to `.env`.

   ```bash
   cp .env.template .env
   ```

2. **Edit the `.env` file:**

   Add your **Telegram Bot Token** (`TELE_API_TOKEN`) and other required variables, such as directories for temporary files (`CACHE_DIR`) and overlays (`PORTRAIT_OVERLAY_FRAME_1_DIR`, etc.).

   Example:

   ```env
   TELE_API_TOKEN=your-telegram-bot-token
   CACHE_DIR=./temp
   PORTRAIT_OVERLAY_FRAME_1_DIR=./overlays/portrait_frame1.png
   PORTRAIT_OVERLAY_FRAME_2_DIR=./overlays/portrait_frame2.png
   LANDSCAPE_OVERLAY_FRAME_1_DIR=./overlays/landscape_frame1.png
   LANDSCAPE_OVERLAY_FRAME_2_DIR=./overlays/landscape_frame2.png
   ```

   Make sure to set up the correct paths for your overlay frames and cache directory.

---

## Running the Bot Locally

1. **Ensure that `ffmpeg` is installed:**

   For **Mac/Linux**:
   ```bash
   brew install ffmpeg
   ```

   For **Windows**, download the executable from [FFmpeg's official site](https://ffmpeg.org/download.html) and add it to your system's PATH.

2. **Start the bot:**

   To start the bot on your local machine, run the following command:

   ```bash
   python src/main.py
   ```

   The bot will start polling for messages. You should now be able to access the bot via the link `t.me/your_bot_username` created when initializing the bot with [@BotFather](https://core.telegram.org/bots#botfather). You can send a video to the bot, and it will process the video and send you two options with different frame overlays.

---

## Hosting the Bot on AWS EC2

To host the bot on an AWS EC2 instance, follow the instructions in the official AWS documentation here: [Getting Started with EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html).

### Steps:
1. **Launch an EC2 instance**:
   - Follow the guide on the AWS documentation to launch an EC2 instance (Ubuntu, Amazon Linux, or any preferred Linux distribution).
   - Ensure your EC2 instance has an appropriate security group allowing SSH (port 22) and any other necessary ports.

2. **Set up your EC2 instance**:
   - SSH into your EC2 instance from your local machine:
     ```bash
     ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-ip
     ```

3. **Install dependencies on the EC2 instance**:
   - Install Python 3.12, `ffmpeg`, and other necessary packages on the EC2 instance:
     ```bash
     sudo apt update
     sudo apt install python3.12 python3-pip ffmpeg git
     ```

4. **Transfer your code to EC2**:
   - You can use SCP to copy your codebase from your local machine to the EC2 instance:
     ```bash
     scp -i /path/to/your-key.pem -r /path/to/your/code ubuntu@your-ec2-public-ip:/home/ubuntu/furious
     ```

5. **Setup environment and run the bot**:
   - SSH into your EC2 instance and navigate to the project directory:
     ```bash
     cd /home/ubuntu/furious
     ```
   - Create a virtual environment:
     ```bash
     python3.12 -m venv venv
     ```
   - Activate the virtual environment:
     ```bash
     source venv/bin/activate
     ```
   - Install the dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Edit the `.env` file on your EC2 instance and set your environment variables.
   - Run the bot:
     ```bash
     python src/main.py
     ```

Now, your bot should be up and running on AWS EC2!

---

## Dependencies

The required dependencies are listed in `requirements.txt`.

To install the dependencies, run:

```bash
pip install -r requirements.txt
```

---

## Contributing

Feel free to fork the repository, create issues, and send pull requests if you’d like to contribute. Please ensure that any contributions follow the existing coding style and include tests when appropriate.

---

If you run into any issues or have questions, feel free to open an issue in the repository.

Enjoy the bot! 🎉🎥

--- 

