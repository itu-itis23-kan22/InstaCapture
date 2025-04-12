# 📱 InstaCapture (InstaStalker)

A user-friendly tool for downloading Instagram content, including stories, posts, reels, and profile pictures.

![InstaCapture Logo](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/logo.png)

> ⚠️ **Important Note**: This project is developed for educational purposes and is designed for personal use only. It is the user's responsibility to ensure compliance with Instagram's terms of service. The developers of this project are not responsible for any misuse or violation of Instagram's terms.

## 📖 Overview

InstaCapture is a Python-based application that allows users to download various Instagram content for offline viewing. The project demonstrates modern Python application development techniques, API integration, and user interface design.

Whether you prefer command-line interfaces or graphical user interfaces, InstaCapture offers both options to accommodate your needs.

## 🌟 Features

- 📸 **Download Stories**: Download stories by username
  - View and save temporary stories before they disappear
  - Save both images and videos from stories
  - Preserve story metadata including timestamps

- 🎬 **Download Posts/Reels**: Download Instagram posts or reels by URL
  - Extract all media from multi-image/video posts
  - Download Reels with original quality
  - Save post captions and metadata

- 👤 **Download Profile Pictures**: Download profile pictures by username
  - Get full-resolution profile pictures
  - Works for both public and private accounts (if cookies are provided)

- 🔄 **Batch Download**: Download all content from a user at once
  - Combined stories and recent posts download
  - Efficient processing with parallel downloads
  - Organized file structure for easy browsing

- 🌐 **Multiple Language Support**: Turkish and English language options
  - Complete interface translation
  - Easily switch between languages from the menu
  - Language settings are saved between sessions

- 🖥️ **CLI and GUI Interface**: Two different usage options based on your needs
  - Powerful command-line interface for scripting and automation
  - User-friendly GUI with intuitive controls and visual feedback
  - Consistent functionality across both interfaces

## 🔍 Screenshots

![CLI Interface](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/cli_screenshot.png)
*Command-line interface showing story download*

![GUI Interface](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/gui_screenshot.png)
*Graphical user interface with download options*

## 📋 Requirements

- Python 3.6 or higher
- The following Python libraries:
  - instacapture: Core functionality for Instagram content downloading
  - requests: For HTTP requests to Instagram servers
  - pillow: Image processing for GUI (optional if using CLI only)
  - tkinter: GUI framework (comes with most Python installations, optional if using CLI only)

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
   - If you encounter a permission error, run `chmod +x InstaCapture.command` in Terminal first
   - If you see a security warning that says "macOS cannot verify that this app is free from malware", you need to:
     1. Open System Preferences > Security & Privacy
     2. Click the lock icon to make changes (enter your password)
     3. Look for the message about "InstaCapture.command" was blocked and click "Open Anyway"
     4. Return to the file and double-click it again, then click "Open" when prompted
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
This will create a shortcut on your desktop based on your operating system, allowing for easy access to the application.

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
8. Paste it into InstaCapture when prompted

![Cookie Instructions](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/cookie_instructions.png)
*How to find the cookie value*

### Downloading Posts/Reels

1. Find the post or reel you want to download on Instagram
2. Copy the URL from your browser address bar
3. Paste the URL into InstaCapture
4. The post and all its media will be downloaded automatically

### Batch Downloading

1. Enter the username you want to batch download from
2. Choose whether to download Stories, Posts, or Both
3. Wait for the download to complete
4. All content will be organized in separate folders

### Location of Downloaded Content

All downloaded files are stored in the `instagram_content` folder:

- `instagram_content/stories/` - Downloaded stories
  - Organized by username
  - Each story has timestamp information
- `instagram_content/posts/` - Downloaded posts and reels
  - Organized by username and post ID
  - Includes JSON metadata files
- `instagram_content/profiles/` - Downloaded profile pictures
  - Organized by username

## ⚠️ Troubleshooting

### Common Issues

1. **"Cookie Error" or "Unable to download stories"**
   - Make sure you've copied the entire cookie string from Instagram
   - Check that your Instagram session is still active
   - Your cookies may have expired; log out and log back into Instagram

2. **"Module not found" errors**
   - Run `pip install -r requirements.txt` to install all dependencies
   - Make sure you're using Python 3.6 or higher

3. **GUI doesn't appear**
   - Ensure Tkinter is installed (it comes with most Python installations)
   - Try running from command line to see if there are any error messages
   - If you see an error message "Please reinstall Python with Tkinter support", follow these instructions:
     - **macOS**: Run `brew install python-tk` or `brew reinstall python`
     - **Linux (Debian/Ubuntu)**: Run `sudo apt-get update && sudo apt-get install python3-tk`
     - **Linux (Fedora)**: Run `sudo dnf install python3-tkinter`
     - **Windows**: Reinstall Python with Tkinter options checked. During installation, select "Customize installation" and ensure "tcl/tk and IDLE" option is selected
   - To test if Tkinter is properly installed, run: `python -c "import tkinter; tkinter._test()"`

4. **PEP 668 error when installing packages**
   - If you see an error message like "See PEP 668 for the detailed specification" when trying to install packages, this is due to Python's system protection
   - This commonly occurs on macOS with Homebrew Python 3.10+ or Linux distributions with system Python
   - Solutions:
     - Create a virtual environment first (recommended):
       ```bash
       python -m venv .venv
       source .venv/bin/activate  # On macOS/Linux
       .venv\Scripts\activate     # On Windows
       pip install pillow requests
       ```
     - Or install packages for your user only:
       ```bash
       pip install --user pillow requests
       ```
     - Or run the command directly with required packages pre-installed:
       ```bash
       python3 instastalk.py  # For CLI
       python3 instastalk_gui.py  # For GUI
       ```

5. **Permission errors on macOS/Linux**
   - Run `chmod +x InstaCapture.command` for macOS
   - Ensure you have write permissions for the destination folder
   - On macOS, if you see "macOS cannot verify that this app is free from malware", follow the steps in the Installation section to allow the app to run (using Security & Privacy settings)

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🔒 Security

- Your cookies are stored only on your own computer, in the `~/.instastalk/cookies.json` file.
- Cookies or your account information are never sent to any server.
- The application only uses cookies to authorize Instagram API requests.
- We recommend using a dedicated Instagram account for testing if you're concerned about security.

## 📝 Educational Project

This project has been developed for educational purposes to enhance Python programming skills, learn API usage, and gain experience in user interface design. It covers the following educational topics:

- HTTP requests and cookie management
- API integration and data parsing
- Multi-language support and internationalization
- Command-line and graphical user interface (GUI) development
- File system operations and data organization
- Python module architecture and project structuring
- Error handling and user feedback

## 🤝 Contributing

Contributions to InstaCapture are welcome! If you'd like to contribute, please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## ❓ FAQ

**Q: Is this tool legal to use?**
A: The tool itself is legal, but how you use it matters. Only download content you have permission to access, and respect copyright laws and Instagram's terms of service.

**Q: Do I need an Instagram account to use this?**
A: Yes, you need an Instagram account and valid cookies to download most content, especially stories.

**Q: How often do I need to update my cookies?**
A: Instagram sessions typically last 1-2 weeks. You'll need to update your cookies when your session expires.

**Q: Can I download content from private accounts?**
A: You can only download content from private accounts that you follow with the account whose cookies you're using.

**Q: Why is the tool not working suddenly?**
A: Instagram frequently updates their API and web interface. If the tool stops working, check for updates to the InstaCapture project.

## 🌐 Other Languages

- [README in Turkish](README.tr.md)
