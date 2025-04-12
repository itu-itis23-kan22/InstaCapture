#!/usr/bin/env python3
"""
InstaCapture Masaüstü Kısayol Kurulum Betiği
--------------------------------------------
Bu betik, kullanıcının masaüstüne InstaCapture kısayolunu ekler.
"""

import os
import sys
import platform
import shutil
from pathlib import Path

def create_windows_shortcut():
    """Windows için masaüstü kısayolu oluştur."""
    try:
        import winshell
        from win32com.client import Dispatch
    except ImportError:
        print("Kısayol oluşturmak için gerekli modüller yükleniyor...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32", "winshell"])
        import winshell
        from win32com.client import Dispatch
    
    desktop = winshell.desktop()
    path = os.path.join(desktop, "InstaCapture.lnk")
    target = os.path.join(os.getcwd(), "StartInstaCapture.bat")
    icon = os.path.join(os.getcwd(), "instagram_content", "icon.ico")
    
    # Simge dosyası yoksa boş bırak
    if not os.path.exists(icon):
        icon = target
    
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.getcwd()
    shortcut.IconLocation = icon
    shortcut.save()
    
    print(f"✅ Kısayol başarıyla oluşturuldu: {path}")

def create_macos_alias():
    """macOS için masaüstü kısayolu (alias) oluştur."""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    app_path = os.path.join(os.getcwd(), "InstaCapture.command")
    
    # Dosyaya çalıştırma izni ver
    os.chmod(app_path, 0o755)
    
    # AppleScript ile alias oluştur
    script = f'''
    tell application "Finder"
        make new alias file to POSIX file "{app_path}" at POSIX file "{desktop_path}"
        set name of result to "InstaCapture"
    end tell
    '''
    
    os.system(f"osascript -e '{script}'")
    print(f"✅ Alias başarıyla oluşturuldu: {os.path.join(desktop_path, 'InstaCapture')}")

def create_linux_desktop_entry():
    """Linux için masaüstü girişi oluştur."""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop_path):
        desktop_path = os.path.join(os.path.expanduser("~"), "Masaüstü")
    
    app_path = os.path.join(os.getcwd(), "InstaCapture.sh")
    
    # Başlatıcı script oluştur
    with open(app_path, 'w') as f:
        f.write('''#!/bin/bash
cd "$(dirname "$0")"
python3 run_gui.py
''')
    
    # Çalıştırma izni ver
    os.chmod(app_path, 0o755)
    
    # Desktop dosyası içeriği
    desktop_entry = f'''[Desktop Entry]
Name=InstaCapture
Comment=Instagram Content Downloader
Exec={app_path}
Icon={os.path.join(os.getcwd(), "instagram_content", "icon.png")}
Terminal=false
Type=Application
Categories=Utility;Network;
'''
    
    # Desktop dosyasını oluştur
    desktop_file = os.path.join(desktop_path, "instacapture.desktop")
    with open(desktop_file, 'w') as f:
        f.write(desktop_entry)
    
    # Çalıştırma izni ver
    os.chmod(desktop_file, 0o755)
    
    print(f"✅ Masaüstü kısayolu başarıyla oluşturuldu: {desktop_file}")

def main():
    """Ana fonksiyon - işletim sistemini tespit et ve ilgili kısayolu oluştur."""
    print("📲 InstaCapture Masaüstü Kısayol Kurulumu")
    print("------------------------------------------")
    
    system = platform.system()
    
    if system == "Windows":
        print("Windows işletim sistemi tespit edildi.")
        create_windows_shortcut()
    elif system == "Darwin":  # macOS
        print("macOS işletim sistemi tespit edildi.")
        create_macos_alias()
    elif system == "Linux":
        print("Linux işletim sistemi tespit edildi.")
        create_linux_desktop_entry()
    else:
        print(f"⚠️ Desteklenmeyen işletim sistemi: {system}")
        print("Lütfen manuel olarak kısayol oluşturun.")
    
    print("\n✨ İşlem tamamlandı! Masaüstünüzde InstaCapture kısayolunu görebilirsiniz.")
    input("Çıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main() 