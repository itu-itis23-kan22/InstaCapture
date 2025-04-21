# InstaCapture

**InstaCapture is a command-line tool for downloading Instagram content including stories, posts, reels, and profile pictures.**

[README in Turkish](README.tr.md)

## 📱 Overview

InstaCapture allows you to download Instagram content for archiving or offline viewing. It provides a simple command-line interface to download stories, posts, and profile pictures from public or private accounts (requires login cookies).

## ✨ Features

- 📸 **Story Downloads**: Save Instagram stories from any user (public or private if you have valid cookies)
- 🖼️ **Post Downloads**: Save photos and videos from posts
- 📹 **Reels Support**: Download Instagram reels
- 👤 **Profile Pictures**: Download profile pictures in full resolution
- 🔄 **Batch Downloads**: Download multiple stories or posts at once
- 🔒 **Private Account Support**: Access content from private accounts you follow
- 🌍 **Multilingual**: Available in English and Turkish
- 🖥️ **Command-Line Interface**: Simple to use from the terminal

## 🔧 Requirements

- Python 3.7 or higher
- Required packages:
  - instacapture
  - pytz
  - requests
  - lxml
  - cryptography
  - brotli

## 📦 Installation & Setup

### Windows
```bash
# Clone the repository
git clone https://github.com/itu-itis23-kan22/InstaCapture.git
cd InstaCapture

# Install required packages
pip install -r requirements.txt

# Run the application
python instastalk.py
```

### macOS / Linux
```bash
# Clone the repository
git clone https://github.com/itu-itis23-kan22/InstaCapture.git
cd InstaCapture

# Install required packages
pip3 install -r requirements.txt

# Run the application
python3 instastalk.py
```

## 📝 Usage

### Downloading Stories
1. Run the application: `python instastalk.py`
2. Enter the username whose stories you want to download
3. The stories will be saved in the `instagram_content/stories/` directory

### Downloading Posts
1. Run the application: `python instastalk.py`
2. Select option 2 to download posts
3. Enter the Instagram post URL (e.g., https://www.instagram.com/p/ABC123/)
4. The post content will be saved in the `instagram_content/posts/` directory

### Batch Downloading
1. Run the application: `python instastalk.py`
2. Select option 6 for batch downloading
3. Enter the username to batch download their stories and posts
4. The content will be organized in the respective directories

### Downloaded Content Location
All downloaded content is saved in the `instagram_content/stories/` directory under the specified username.