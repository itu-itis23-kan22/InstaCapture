#!/usr/bin/env python3
"""
InstaCapture Başlatıcı (Windows)
--------------------------------
Bu dosya, Windows'ta komut satırı penceresi göstermeden uygulamayı başlatır.
Sadece bu dosyaya çift tıklamak yeterlidir.
"""

import os
import sys
import subprocess
import platform
import webbrowser
import threading

def show_message(message, type="info"):
    """Mesaj göster - gerekirse dialog kullanarak."""
    try:
        # GUI ile mesaj göster
        import ctypes
        if type == "error":
            icon = 0x10  # MB_ICONERROR
            title = "Hata"
        else:
            icon = 0x40  # MB_ICONINFORMATION
            title = "Bilgi"
        ctypes.windll.user32.MessageBoxW(0, message, title, icon)
    except:
        # Fallback - sadece yazdır
        print(message)

def check_requirements():
    """Gerekli paketlerin yüklü olup olmadığını kontrol et."""
    try:
        import tkinter
        
        # Gerekli paketleri arka planda yükle
        def install_packages():
            try:
                # Pillow paketi
                try:
                    from PIL import Image
                except ImportError:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"], 
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Requests paketi
                try:
                    import requests
                except ImportError:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], 
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # lxml paketi
                try:
                    import lxml
                except ImportError:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "lxml"], 
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                show_message(f"Paket kurulumu sırasında bir hata oluştu: {str(e)}", "error")
        
        # Paketleri arka planda yükle
        threading.Thread(target=install_packages, daemon=True).start()
        return True
        
    except ImportError:
        show_message("Tkinter paketi bulunamadı. Lütfen Python'u Tkinter desteğiyle yeniden yükleyin.", "error")
        webbrowser.open("https://www.python.org/downloads/")
        return False
    except Exception as e:
        show_message(f"Paket kontrolü sırasında bir hata oluştu: {str(e)}", "error")
        return False

def main():
    """Ana fonksiyon."""
    # Çalışma dizinini script'in bulunduğu dizine değiştir
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Gereksinimleri kontrol et
    if not check_requirements():
        return
    
    # GUI başlatmayı dene
    try:
        if os.path.exists("instastalk_gui.py"):
            # GUI modülünü doğrudan içe aktar
            import instastalk_gui
            instastalk_gui.main()
        elif os.path.exists("run_gui.py"):
            # run_gui.py betiğini çalıştır
            subprocess.run([sys.executable, "run_gui.py"], 
                          creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0)
        else:
            # Alternatif olarak ana modülü GUI modunda başlat
            from instastalk import main as instastalk_main
            sys.argv.append("--gui")
            instastalk_main()
    
    except Exception as e:
        error_message = f"Uygulama başlatılırken bir hata oluştu: {str(e)}"
        show_message(error_message, "error")

if __name__ == "__main__":
    main() 