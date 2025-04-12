# 📱 InstaCapture (InstaStalker)

A user-friendly tool for downloading Instagram content.

> ⚠️ **Important Note**: This project is developed for educational purposes and is designed for personal use only. It is the user's responsibility to ensure compliance with Instagram's terms of service.

## 🌟 Features

- 📸 **Download Stories**: Download stories by username
- 🎬 **Download Posts/Reels**: Download Instagram posts or reels by URL
- 👤 **Download Profile Pictures**: Download profile pictures by username
- 🔄 **Batch Download**: Download all content from a user at once
- 🌐 **Multiple Language Support**: Turkish and English language options
- 🖥️ **CLI and GUI Interface**: Two different usage options based on your needs

## 📋 Requirements

- Python 3.6 or higher
- The following Python libraries:
  - instacapture
  - requests
  - pillow (for GUI)
  - tkinter (for GUI)

## 🚀 Installation and Setup

### Installing Packages
```bash
# Install required libraries
pip install instacapture requests pillow
```

### For Windows Users
1. Double-click on `InstaCapture.pyw` or `StartInstaCapture.bat` in the downloaded files.
2. Alternatively, in command prompt:
```bash
python instastalk.py        # For command-line interface
python instastalk_gui.py    # For graphical interface
```

### For macOS Users
1. Double-click on `InstaCapture.command` in the downloaded files.
2. Alternatively, in Terminal:
```bash
python3 instastalk.py       # For command-line interface
python3 instastalk_gui.py   # For graphical interface
```

### For Linux Users
In Terminal:
```bash
python3 instastalk.py       # For command-line interface
python3 instastalk_gui.py   # For graphical interface
```

### Creating Desktop Shortcut for Easy Access
To create a desktop shortcut:
```bash
python desktop_shortcut_setup.py
```

## 🔧 Usage

### Downloading Stories

To download stories, you need to set your Instagram cookies:

1. Go to Instagram.com in Chrome/Safari and log in
2. Right-click anywhere on the page and select 'Inspect'
3. Click on the 'Network' tab in the developer tools
4. Refresh the page (F5)
5. Select a request that starts with 'instagram.com'
6. Find the 'Cookie:' line in the 'Request Headers' section of the 'Headers' tab
7. Copy the entire cookie line

### Location of Downloaded Content

All downloaded files are stored in the `instagram_content` folder:

- `instagram_content/stories/` - Downloaded stories
- `instagram_content/posts/` - Downloaded posts and reels
- `instagram_content/profiles/` - Downloaded profile pictures

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🔒 Security

- Your cookies are stored only on your own computer, in the `~/.instastalk/cookies.json` file.
- Cookies or your account information are never sent to any server.
- The application only uses cookies to authorize Instagram API requests.

## 📝 Educational Project

This project has been developed for educational purposes to enhance Python programming skills, learn API usage, and gain experience in user interface design. It covers the following educational topics:

- HTTP requests and cookie management
- API integration
- Multi-language support
- Command-line and graphical user interface (GUI) development
- File system operations
- Python module architecture 