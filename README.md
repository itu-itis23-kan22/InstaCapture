# InstaCapture

![InstaCapture Logo](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/logo.png)

**InstaCapture is a command-line tool for downloading Instagram content including stories, posts, reels, and profile pictures.**

[README in Turkish](README.tr.md)

## 📱 Overview

InstaCapture allows you to download Instagram content for archiving or offline viewing. It provides a simple command-line interface to download stories, posts, and profile pictures from public or private accounts (requires login cookies).

## ✨ Features

- 📸 **Story Downloads**: Save stories from any user you follow
- 🖼️ **Post Downloads**: Save photos and videos from posts
- 📹 **Reels Support**: Download Instagram reels
- 👤 **Profile Pictures**: Download profile pictures in full resolution
- 🔄 **Batch Downloads**: Download multiple stories or posts at once
- 🔒 **Private Account Support**: Access content from private accounts you follow
- 🌍 **Multilingual**: Available in English and Turkish
- 🖥️ **Command-Line Interface**: Simple to use from the terminal

![CLI Screenshot](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/cli_screenshot.png)

## 🔧 Requirements

- Python 3.7 or higher
- Required packages:
  - instacapture
  - pytz
  - requests
  - lxml

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
2. Select option 1 to download stories
3. Enter the username whose stories you want to download
4. The stories will be saved in the `instagram_content/stories/` directory

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
All downloaded content is saved in the `instagram_content/` directory, organized by content type:
- Stories: `instagram_content/stories/`
- Posts: `instagram_content/posts/`
- Profile Pictures: `instagram_content/profile_pics/`
- Highlights: `instagram_content/highlights/`

## 🔍 Troubleshooting

1. **Cookies Required**
   - To access content from private accounts or accounts you follow, you need to provide Instagram cookies
   - In the application, select option 4 to set cookies
   - Follow the instructions to copy your Instagram cookies

2. **Content Not Found**
   - Ensure you have the correct username or URL
   - Check that you have access to view the content
   - Verify that your cookies are valid and not expired

## 🔐 Security Note

InstaCapture stores Instagram cookies locally to allow access to content from private accounts. These cookies are stored in the `.instastalk/cookies.json` file. Never share your cookies with others as they can be used to access your Instagram account.

## 🤝 Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or code contributions, please feel free to contribute.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For detailed information on contributing, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## ❓ FAQ

**Is this tool legal?**
InstaCapture is designed for personal use only to download content you already have access to view. Use it responsibly and respect Instagram's Terms of Service.

**Do I need an Instagram account?**
Yes, to access most content, especially from private accounts, you need to log in with valid Instagram cookies.

**Why do my cookies expire?**
Instagram cookies typically expire after a few days. If you encounter issues, simply update your cookies using option 4 in the application.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
