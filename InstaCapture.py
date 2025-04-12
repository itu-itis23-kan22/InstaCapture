#!/usr/bin/env python3
"""
InstaCapture Başlatıcı
----------------------
Bu basit launcher, InstaCapture uygulamasını başlatır.

Kullanıcı dostu arayüz için sadece bu dosyaya çift tıklamak yeterlidir.
"""

import os
import sys
import subprocess
import platform
import webbrowser

def show_message(message, type="info"):
    """Mesaj göster - gerekirse dialog kullanarak."""
    try:
        # GUI ile mesaj göster
        if platform.system() == "Windows":
            import ctypes
            if type == "error":
                icon = 0x10  # MB_ICONERROR
                title = "Hata"
            else:
                icon = 0x40  # MB_ICONINFORMATION
                title = "Bilgi"
            ctypes.windll.user32.MessageBoxW(0, message, title, icon)
        elif platform.system() == "Darwin":  # macOS
            os.system(f'osascript -e \'display dialog "{message}" buttons {{"Tamam"}} default button "Tamam"\'')
        else:
            # Terminalde göster
            color = "\033[91m" if type == "error" else "\033[92m"
            print(f"{color}{message}\033[0m")
    except:
        # Fallback - sadece yazdır
        print(message)

def check_requirements():
    """Gerekli paketlerin yüklü olup olmadığını kontrol et."""
    try:
        import tkinter
        # Pillow paketi
        try:
            from PIL import Image
        except ImportError:
            print("Pillow paketi yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            
        # Requests paketi
        try:
            import requests
        except ImportError:
            print("Requests paketi yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            
        # lxml paketi
        try:
            import lxml
        except ImportError:
            print("lxml paketi yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "lxml"])
            
        return True
        
    except ImportError:
        show_message("Tkinter paketi bulunamadı. Lütfen Python'u Tkinter desteğiyle yeniden yükleyin.", "error")
        webbrowser.open("https://www.python.org/downloads/")
        return False
    except Exception as e:
        show_message(f"Paket kurulumu sırasında bir hata oluştu: {str(e)}", "error")
        return False

def main():
    """Ana fonksiyon."""
    print("📲 InstaCapture - Instagram İçerik İndirme Aracı başlatılıyor...")
    
    # Çalışma dizinini script'in bulunduğu dizine değiştir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Gereksinimleri kontrol et
    if not check_requirements():
        input("Çıkmak için Enter tuşuna basın...")
        return
    
    # GUI başlatmayı dene
    try:
        if os.path.exists("instastalk_gui.py"):
            # GUI modülünü doğrudan içe aktar
            import instastalk_gui
            instastalk_gui.main()
        elif os.path.exists("run_gui.py"):
            # run_gui.py betiğini çalıştır
            subprocess.run([sys.executable, "run_gui.py"])
        else:
            # Alternatif olarak ana modülü GUI modunda başlat
            from instastalk import main as instastalk_main
            sys.argv.append("--gui")
            instastalk_main()
    
    except Exception as e:
        error_message = f"Uygulama başlatılırken bir hata oluştu: {str(e)}"
        show_message(error_message, "error")
        print(error_message)
        input("Çıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    main() 