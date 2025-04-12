#!/usr/bin/env python3
"""
InstaStalk GUI başlatma betiği
-----------------------------
Bu betik, InstaStalk GUI uygulamasını başlatır.
"""

import os
import sys
import subprocess

def main():
    """GUI uygulamasını başlat."""
    try:
        # İhtiyaç duyulan paketleri kontrol et ve kur
        packages = ["pillow", "requests"]
        for package in packages:
            try:
                __import__(package.split("[")[0])
            except ImportError:
                print(f"{package} paketi kuruluyor...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        
        # GUI uygulamasını başlat
        if os.path.exists("instastalk_gui.py"):
            print("GUI başlatılıyor...")
            import instastalk_gui
            instastalk_gui.main()
        else:
            # Alternatif olarak instastalk.py dosyasını --gui parametresiyle çalıştır
            print("GUI dosyası bulunamadı, ana uygulama üzerinden başlatılıyor...")
            from instastalk import main
            sys.argv.append("--gui")
            main()
            
    except Exception as e:
        print(f"Hata: {str(e)}")
        print("\nGUI başlatılamadı. Lütfen aşağıdaki paketlerin kurulu olduğundan emin olun:")
        print("- pillow")
        print("- requests")
        print("\n'pip install pillow requests' komutunu çalıştırarak gerekli paketleri kurabilirsiniz.")
        
        # Hatayı göster ve çıkış yapmadan önce bekle
        input("\nÇıkmak için Enter tuşuna basın...")


if __name__ == "__main__":
    main() 