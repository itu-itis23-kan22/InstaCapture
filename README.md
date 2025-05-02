# InstaCapture

**InstaCapture is a command-line tool for downloading Instagram stories.**

[README in Turkish](README.tr.md)

## 📱 Overview

InstaCapture allows you to download Instagram stories for archiving or offline viewing. It provides a simple command-line interface to download stories from public or private accounts (requires valid login cookies).

## ✨ Features

- 📸 **Story Downloads**: Save Instagram stories from any user with valid cookies.
- 🌍 **Multilingual**: Available in English and Turkish.
- 🖥️ **Command-Line Interface**: Simple to use from the terminal.

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

1. Run the application:
   ```bash
   python instastalk.py
   ```
2. Choose an option:
   - 1. **Story Stalk**: Enter a username to download their stories.
   - 2. **Change Cookies**: Paste new Instagram login cookies.
   - 3. **Change Language (Dil Değiştir)**: Switch between Turkish and English.
   - 0. **Exit**: Close the application.

### Download Location

All downloaded stories are saved under the `instagram_content/stories/<username>/` directory.