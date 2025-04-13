#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from pathlib import Path
import json
import webbrowser
import re

# Paket yükleme fonksiyonu
def install_package(package_name):
    print(f"{package_name} paketi yükleniyor...")
    methods = [
        [sys.executable, "-m", "pip", "install", package_name],
        ["pip", "install", package_name],
        ["pip3", "install", package_name]
    ]
    
    for cmd in methods:
        try:
            subprocess.check_call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"{package_name} başarıyla yüklendi!")
            return True
        except:
            continue
    
    return False

# Gerekli paketleri yüklemeyi dene
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext
except ImportError as e:
    print("Tkinter paketi bulunamadı. Bu Python kurulumunuzla gelmelidir.")
    print("Lütfen Python'u Tkinter desteğiyle yeniden kurun.")
    sys.exit(1)

# Diğer paketleri kontrol et ve yüklemeyi dene
required_packages = ["pillow", "requests", "lxml"]
missing_packages = []

# Threading modülü
try:
    import threading
except ImportError:
    missing_packages.append("threading")

# PIL modülü
try:
    from PIL import Image, ImageTk
except ImportError:
    missing_packages.append("pillow")
    
# Requests modülü  
try:
    import requests
except ImportError:
    missing_packages.append("requests")

# lxml modülü (isteğe bağlı ama yararlı)
try:
    import lxml
except ImportError:
    missing_packages.append("lxml")

# Eksik paketleri yüklemeyi dene
if missing_packages:
    print(f"Eksik paketler bulundu: {', '.join(missing_packages)}")
    print("Paketler otomatik olarak yüklenmeye çalışılacak...")
    
    success = True
    for package in missing_packages:
        if not install_package(package):
            success = False
            print(f"{package} paketi yüklenemedi.")
    
    if not success:
        print("\nBazı paketler yüklenemedi.")
        print("Lütfen manuel olarak şu komutu çalıştırın:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)
    
    print("Paketler yüklendi, modüller içe aktarılıyor...")
    
    # Yeniden import etmeyi dene
    try:
        if "pillow" in missing_packages:
            from PIL import Image, ImageTk
        if "requests" in missing_packages:
            import requests
        if "lxml" in missing_packages:
            import lxml
        if "threading" in missing_packages:
            import threading
    except ImportError as e:
        print(f"Paketler yüklendikten sonra bile import hatası: {e}")
        print("Lütfen uygulamayı yeniden başlatın.")
        sys.exit(1)

# InstaStalk sınıfını içe aktar
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
try:
    from instastalk import InstaStalker, TRANSLATIONS
except ImportError as e:
    print(f"instastalk.py dosyası bulunamadı veya içe aktarılamadı: {e}")
    print("Lütfen instastalk.py dosyasının bu script ile aynı klasörde olduğundan emin olun.")
    sys.exit(1)

class InstaStalkGUI(tk.Tk):
    """InstaStalker için grafik arayüz."""
    
    def __init__(self):
        super().__init__()
        
        # Ana uygulama nesnesi oluştur
        self.stalker = InstaStalker()
        
        # Ana pencere ayarları
        self.title("InstaStalker - Instagram İçerik İndirme Aracı")
        self.geometry("800x600")
        self.minsize(800, 600)
        
        # Stil ayarları
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')  # Tema seç (diğer seçenekler: 'alt', 'default', 'classic')
        except:
            # Tema bulunamazsa devam et
            pass
        
        # Tema Renkleri
        self.bg_color = "#f0f2f5"
        self.header_color = "#1877F2"
        self.button_color = "#1877F2"
        self.highlight_color = "#E7F3FF"
        
        # Özel stiller tanımla
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Header.TFrame', background=self.header_color)
        self.style.configure('TLabel', background=self.bg_color, font=('Helvetica', 10))
        self.style.configure('Header.TLabel', background=self.header_color, foreground='white', font=('Helvetica', 14, 'bold'))
        self.style.configure('Title.TLabel', background=self.bg_color, font=('Helvetica', 16, 'bold'))
        self.style.configure('TButton', background=self.button_color, foreground='black')
        self.style.map('TButton', background=[('active', self.highlight_color)])
        
        # Ana çerçeveleri oluştur
        self.create_main_frames()
        
        # Menü oluştur
        self.create_menu()
        
        # Içerik oluştur
        self.create_content()
        
        # Çerezleri yükle
        if self.stalker.load_cookies():
            self.update_status(self._("cookies_loaded", self.stalker.cookies_file))
        
        # Dil değişikliklerini dinle
        self.bind("<<LanguageChanged>>", self.refresh_language)
        
        # Pencere kapatılırken olayını yakala
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def _(self, key, *args):
        """Dil çevirisi yapar."""
        return self.stalker._(key, *args)
        
    def create_main_frames(self):
        """Ana çerçeveleri oluştur."""
        # Üst çerçeve - başlık ve logo
        self.header_frame = ttk.Frame(self, style='Header.TFrame')
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Logo ve başlık
        self.logo_label = ttk.Label(self.header_frame, text="📲", style='Header.TLabel', font=('Helvetica', 24))
        self.logo_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.title_label = ttk.Label(self.header_frame, text="InstaStalker", style='Header.TLabel')
        self.title_label.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Dil seçimi
        self.lang_var = tk.StringVar(value=self.stalker.settings.get("language", "tr"))
        self.lang_menu = ttk.Combobox(self.header_frame, textvariable=self.lang_var, values=["tr", "en"], width=5, state="readonly")
        self.lang_menu.pack(side=tk.RIGHT, padx=10, pady=10)
        self.lang_menu.bind("<<ComboboxSelected>>", self.change_language)
        
        # Ana içerik alanı
        self.content_frame = ttk.Frame(self, style='TFrame')
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Alt bilgi çerçevesi
        self.footer_frame = ttk.Frame(self, style='TFrame')
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Durum çubuğu
        self.status_var = tk.StringVar(value="")
        self.status_bar = ttk.Label(self.footer_frame, textvariable=self.status_var, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_menu(self):
        """Menü çubuğu oluştur."""
        self.menu_bar = tk.Menu(self)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Set Cookies", command=self.show_cookies_dialog)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_close)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Tools menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.tools_menu.add_command(label="List Downloads", command=self.show_downloads)
        self.tools_menu.add_command(label="Clean All Downloads", command=self.clean_downloads)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        # Menüyü pencereye bağla
        self.config(menu=self.menu_bar)
    
    def create_content(self):
        """Ana içerik alanını oluştur."""
        # Tab kontrolü
        self.tab_control = ttk.Notebook(self.content_frame)
        
        # Hikaye indirme sekmesi
        self.story_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.story_tab, text="Hikayeler")
        
        # Gönderi indirme sekmesi
        self.post_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.post_tab, text="Gönderiler")
        
        # Profil indirme sekmesi
        self.profile_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.profile_tab, text="Profil Resmi")
        
        # Toplu indirme sekmesi
        self.batch_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.batch_tab, text="Toplu İndirme")
        
        # Öne Çıkan Hikayeler sekmesi
        self.highlights_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.highlights_tab, text="Öne Çıkanlar")
        
        # Log sekmesi
        self.log_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.log_tab, text="Log")
        
        # Tab kontrolünü yerleştir
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Sekme içeriklerini oluştur
        self.create_story_tab()
        self.create_post_tab()
        self.create_profile_tab()
        self.create_batch_tab()
        self.create_highlights_tab()
        self.create_log_tab()
    
    def create_story_tab(self):
        """Hikaye indirme sekmesini oluştur."""
        # Kullanıcı adı etiketi ve giriş alanı
        username_frame = ttk.Frame(self.story_tab)
        username_frame.pack(fill=tk.X, padx=20, pady=20)
        
        username_label = ttk.Label(username_frame, text="Kullanıcı Adı:")
        username_label.pack(side=tk.LEFT, padx=5)
        
        self.story_username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.story_username_var, width=30)
        username_entry.pack(side=tk.LEFT, padx=5)
        
        # İndirme butonu
        download_button = ttk.Button(username_frame, text="Hikayeleri İndir", command=self.download_story)
        download_button.pack(side=tk.LEFT, padx=10)
        
        # Sonuç alanı
        result_frame = ttk.LabelFrame(self.story_tab, text="Sonuçlar")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.story_result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=15)
        self.story_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.story_result_text.config(state=tk.DISABLED)
    
    def create_post_tab(self):
        """Gönderi indirme sekmesini oluştur."""
        # URL etiketi ve giriş alanı
        url_frame = ttk.Frame(self.post_tab)
        url_frame.pack(fill=tk.X, padx=20, pady=20)
        
        url_label = ttk.Label(url_frame, text="Gönderi URL:")
        url_label.pack(side=tk.LEFT, padx=5)
        
        self.post_url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.post_url_var, width=50)
        url_entry.pack(side=tk.LEFT, padx=5)
        
        # İndirme butonu
        download_button = ttk.Button(url_frame, text="Gönderiyi İndir", command=self.download_post)
        download_button.pack(side=tk.LEFT, padx=10)
        
        # Sonuç alanı
        result_frame = ttk.LabelFrame(self.post_tab, text="Sonuçlar")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.post_result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=15)
        self.post_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.post_result_text.config(state=tk.DISABLED)
    
    def create_profile_tab(self):
        """Profil indirme sekmesini oluştur."""
        # Kullanıcı adı etiketi ve giriş alanı
        username_frame = ttk.Frame(self.profile_tab)
        username_frame.pack(fill=tk.X, padx=20, pady=20)
        
        username_label = ttk.Label(username_frame, text="Kullanıcı Adı:")
        username_label.pack(side=tk.LEFT, padx=5)
        
        self.profile_username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.profile_username_var, width=30)
        username_entry.pack(side=tk.LEFT, padx=5)
        
        # İndirme butonu
        download_button = ttk.Button(username_frame, text="Profil Resmini İndir", command=self.download_profile)
        download_button.pack(side=tk.LEFT, padx=10)
        
        # Sonuç alanı
        result_frame = ttk.LabelFrame(self.profile_tab, text="Sonuçlar")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Resim gösterme alanı
        self.profile_image_frame = ttk.Frame(result_frame)
        self.profile_image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.profile_image_label = ttk.Label(self.profile_image_frame)
        self.profile_image_label.pack(expand=True)
        
        self.profile_result_var = tk.StringVar()
        profile_result_label = ttk.Label(self.profile_image_frame, textvariable=self.profile_result_var)
        profile_result_label.pack(pady=10)
    
    def create_batch_tab(self):
        """Toplu indirme sekmesini oluştur."""
        # Kullanıcı adı etiketi ve giriş alanı
        username_frame = ttk.Frame(self.batch_tab)
        username_frame.pack(fill=tk.X, padx=20, pady=20)
        
        username_label = ttk.Label(username_frame, text="Kullanıcı Adı:")
        username_label.pack(side=tk.LEFT, padx=5)
        
        self.batch_username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.batch_username_var, width=30)
        username_entry.pack(side=tk.LEFT, padx=5)
        
        # İndirme seçenekleri
        options_frame = ttk.Frame(self.batch_tab)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.batch_option_var = tk.IntVar(value=3)  # Varsayılan: Her ikisi
        
        stories_radio = ttk.Radiobutton(options_frame, text="Sadece Hikayeler", variable=self.batch_option_var, value=1)
        stories_radio.pack(side=tk.LEFT, padx=10)
        
        posts_radio = ttk.Radiobutton(options_frame, text="Sadece Gönderiler", variable=self.batch_option_var, value=2)
        posts_radio.pack(side=tk.LEFT, padx=10)
        
        both_radio = ttk.Radiobutton(options_frame, text="Her İkisi de", variable=self.batch_option_var, value=3)
        both_radio.pack(side=tk.LEFT, padx=10)
        
        # İndirme butonu
        button_frame = ttk.Frame(self.batch_tab)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        download_button = ttk.Button(button_frame, text="Toplu İndir", command=self.download_batch)
        download_button.pack(padx=10)
        
        # Sonuç alanı
        result_frame = ttk.LabelFrame(self.batch_tab, text="Sonuçlar")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.batch_result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, height=15)
        self.batch_result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.batch_result_text.config(state=tk.DISABLED)
    
    def create_highlights_tab(self):
        """Öne çıkan hikayeler sekmesini oluştur."""
        # İçerik çerçevesi
        content_frame = ttk.Frame(self.highlights_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ttk.Label(content_frame, text="Öne Çıkan Hikayeleri İndir", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Kullanıcı adı girişi
        username_frame = ttk.Frame(content_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="Kullanıcı Adı:", width=15)
        username_label.pack(side=tk.LEFT)
        
        self.highlights_username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.highlights_username_var, width=30)
        username_entry.pack(side=tk.LEFT, padx=5)
        
        # İndirme butonu
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        download_button = ttk.Button(button_frame, text="Öne Çıkanları Listele", command=self.fetch_highlights)
        download_button.pack(side=tk.LEFT, padx=5)
        
        # Sonuç alanı
        result_frame = ttk.Frame(content_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Highlights listesi
        self.highlights_listbox_frame = ttk.LabelFrame(result_frame, text="Öne Çıkan Hikayeler")
        self.highlights_listbox_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)
        
        self.highlights_listbox = tk.Listbox(self.highlights_listbox_frame, selectmode=tk.SINGLE, height=10)
        self.highlights_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        highlights_scrollbar = ttk.Scrollbar(self.highlights_listbox_frame, orient=tk.VERTICAL, command=self.highlights_listbox.yview)
        highlights_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.highlights_listbox.config(yscrollcommand=highlights_scrollbar.set)
        
        # İndirme butonları
        button_frame2 = ttk.Frame(result_frame)
        button_frame2.pack(fill=tk.BOTH, side=tk.LEFT, padx=5, pady=5)
        
        self.download_selected_button = ttk.Button(button_frame2, text="Seçileni İndir", 
                                                 command=self.download_selected_highlight, state=tk.DISABLED)
        self.download_selected_button.pack(pady=5, fill=tk.X)
        
        self.download_all_button = ttk.Button(button_frame2, text="Tümünü İndir", 
                                            command=self.download_all_highlights, state=tk.DISABLED)
        self.download_all_button.pack(pady=5, fill=tk.X)
        
        # Sonuç metni
        result_label = ttk.Label(content_frame, text="Sonuçlar:")
        result_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.highlights_result_text = scrolledtext.ScrolledText(content_frame, height=8)
        self.highlights_result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.highlights_result_text.config(state=tk.DISABLED)
    
    def create_log_tab(self):
        """Log sekmesini oluştur."""
        self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.config(state=tk.DISABLED)
        
        # Clear log butonu
        clear_button = ttk.Button(self.log_tab, text="Log Temizle", command=self.clear_log)
        clear_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def update_status(self, message):
        """Durum çubuğunu güncelle."""
        self.status_var.set(message)
        self.update_log(message)
    
    def update_log(self, message):
        """Log metnini güncelle."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)  # Son satıra kaydır
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Log metnini temizle."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def update_result_text(self, text_widget, message):
        """Sonuç metin alanını güncelle."""
        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, f"{message}\n")
        text_widget.see(tk.END)  # Son satıra kaydır
        text_widget.config(state=tk.DISABLED)
        
        # Durum çubuğunu ve log alanını da güncelle
        self.update_status(message)
    
    def capture_output(self, func):
        """Çıktıyı yakala."""
        from io import StringIO
        import sys
        
        # Mevcut stdout'u kaydet
        old_stdout = sys.stdout
        
        # Yeni bir StringIO nesnesi oluştur ve stdout olarak ayarla
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        try:
            # Fonksiyonu çalıştır
            result = func()
            
            # Çıktıyı al
            output = redirected_output.getvalue()
            
            return result, output
        finally:
            # Eski stdout'a geri dön
            sys.stdout = old_stdout
    
    def show_cookies_dialog(self):
        """Çerezleri ayarla dialog'unu göster."""
        dialog = tk.Toplevel(self)
        dialog.title("Instagram Çerezleri")
        dialog.geometry("600x500")
        dialog.transient(self)  # Ana pencereye bağlı
        dialog.grab_set()  # Modalı zorunlu kıl
        
        # Çerezler hakkında bilgi metni
        info_frame = ttk.LabelFrame(dialog, text="Çerezler Nasıl Alınır")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, height=12)
        info_text.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Adımları dil tercihine göre ekle
        cookie_steps = self._("cookie_steps")
        info_text.insert(tk.END, self._("cookies_needed") + "\n\n")
        for step in cookie_steps:
            info_text.insert(tk.END, f"{step}\n")
        
        info_text.config(state=tk.DISABLED)
        
        # Çerez giriş alanı
        cookie_frame = ttk.LabelFrame(dialog, text="Cookie Değeri")
        cookie_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.cookie_text = scrolledtext.ScrolledText(cookie_frame, wrap=tk.WORD, height=10)
        self.cookie_text.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Mevcut çerezleri yükle
        if self.stalker.cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.stalker.cookies.items()])
            self.cookie_text.insert(tk.END, cookie_str)
        
        # Butonlar
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        save_button = ttk.Button(button_frame, text="Kaydet", command=lambda: self.save_cookies())
        save_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="İptal", command=dialog.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Dialog'u ortala
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def save_cookies(self):
        """Çerezleri kaydet."""
        cookie_str = self.cookie_text.get(1.0, tk.END).strip()
        
        if not cookie_str:
            messagebox.showerror("Hata", "Lütfen geçerli bir cookie değeri girin!")
            return
        
        if self.stalker.set_cookies_from_string(cookie_str):
            messagebox.showinfo("Başarılı", "Çerezler başarıyla kaydedildi!")
            self.update_status(self._("cookies_saved", self.stalker.cookies_file))
        else:
            messagebox.showerror("Hata", "Çerezler kaydedilemedi! Lütfen geçerli bir cookie değeri girdiğinizden emin olun.")
    
    def download_story(self):
        """Hikaye indirme işlemini başlat."""
        username = self.story_username_var.get().strip()
        
        if not username:
            messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin!")
            return
        
        # Sonuç alanını temizle
        self.story_result_text.config(state=tk.NORMAL)
        self.story_result_text.delete(1.0, tk.END)
        self.story_result_text.config(state=tk.DISABLED)
        
        # İndirme işlemini arka planda başlat
        threading.Thread(target=self._download_story, args=(username,), daemon=True).start()
    
    def _download_story(self, username):
        """Hikayeleri indir."""
        try:
            self.update_result_text(self.story_result_text, self._("downloading_stories", username))
            
            # Çıktıyı yakalamak için işlevi çağır
            result, output = self.capture_output(lambda: self.stalker.download_story(username))
            
            # Çıktıyı ekrana yazdır
            for line in output.split('\n'):
                if line.strip():
                    self.update_result_text(self.story_result_text, line)
            
        except Exception as e:
            self.update_result_text(self.story_result_text, f"❌ Hata: {str(e)}")
    
    def download_post(self):
        """Gönderi indirme işlemini başlat."""
        post_url = self.post_url_var.get().strip()
        
        if not post_url:
            messagebox.showerror("Hata", "Lütfen bir gönderi URL'si girin!")
            return
        
        # Sonuç alanını temizle
        self.post_result_text.config(state=tk.NORMAL)
        self.post_result_text.delete(1.0, tk.END)
        self.post_result_text.config(state=tk.DISABLED)
        
        # İndirme işlemini arka planda başlat
        threading.Thread(target=self._download_post, args=(post_url,), daemon=True).start()
    
    def _download_post(self, post_url):
        """Gönderiyi indir."""
        try:
            self.update_result_text(self.post_result_text, self._("downloading_post", post_url))
            
            # Çıktıyı yakalamak için işlevi çağır
            result, output = self.capture_output(lambda: self.stalker.download_post(post_url))
            
            # Çıktıyı ekrana yazdır
            for line in output.split('\n'):
                if line.strip():
                    self.update_result_text(self.post_result_text, line)
            
        except Exception as e:
            self.update_result_text(self.post_result_text, f"❌ Hata: {str(e)}")
    
    def download_profile(self):
        """Profil indirme işlemini başlat."""
        username = self.profile_username_var.get().strip()
        
        if not username:
            messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin!")
            return
        
        # Resmi temizle
        self.profile_image_label.config(image="")
        self.profile_result_var.set("")
        
        # İndirme işlemini arka planda başlat
        threading.Thread(target=self._download_profile, args=(username,), daemon=True).start()
    
    def _download_profile(self, username):
        """Profil resmini indir."""
        try:
            self.update_status(self._("downloading_profile", username))
            
            # Çıktıyı yakalamak için işlevi çağır
            result, output = self.capture_output(lambda: self.stalker.download_profile_picture(username))
            
            # Çıktıyı log'a yazdır
            for line in output.split('\n'):
                if line.strip():
                    self.update_log(line)
            
            # İndirilen profil resmini göster
            image_path = None
            for line in output.split('\n'):
                if "saved to" in line:
                    image_path = line.split("'")[1]
                    break
            
            if image_path and Path(image_path).exists():
                self.profile_result_var.set(self._("profile_success", username))
                
                # Resmi yükle ve göster
                try:
                    image = Image.open(image_path)
                    image = image.resize((200, 200), Image.LANCZOS)  # Resmi yeniden boyutlandır
                    photo = ImageTk.PhotoImage(image)
                    self.profile_image_label.config(image=photo)
                    self.profile_image_label.image = photo  # Referansı sakla
                except Exception as e:
                    self.profile_result_var.set(f"Resim gösterilemiyor: {str(e)}")
            else:
                self.profile_result_var.set(self._("profile_not_found", username))
            
        except Exception as e:
            self.profile_result_var.set(f"❌ Hata: {str(e)}")
            self.update_log(f"Profil indirme hatası: {str(e)}")
    
    def download_batch(self):
        """Toplu indirme işlemini başlat."""
        username = self.batch_username_var.get().strip()
        option = self.batch_option_var.get()
        
        if not username:
            messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin!")
            return
        
        # Sonuç alanını temizle
        self.batch_result_text.config(state=tk.NORMAL)
        self.batch_result_text.delete(1.0, tk.END)
        self.batch_result_text.config(state=tk.DISABLED)
        
        # İndirme işlemini arka planda başlat
        threading.Thread(target=self._download_batch, args=(username, option), daemon=True).start()
    
    def _download_batch(self, username, option):
        """Toplu indirme yap."""
        try:
            # Seçilen seçeneği string'e dönüştür
            choice = str(option)
            
            # InstaStalker sınıfında _download_batch metodunu taklit et
            self.update_result_text(self.batch_result_text, self._("batch_download_start", username))
            
            success = True
            
            # Hikayeleri indir
            if choice in ["1", "3"]:
                self.update_result_text(self.batch_result_text, self._("downloading_stories", username))
                _, output = self.capture_output(lambda: self.stalker.download_story(username))
                
                # Çıktıyı ekrana yazdır
                for line in output.split('\n'):
                    if line.strip():
                        self.update_result_text(self.batch_result_text, line)
                
                # Başarı durumunu kontrol et
                if "not found" in output or "error" in output.lower():
                    success = False
            
            # Son gönderileri indir
            if choice in ["2", "3"]:
                self.update_result_text(self.batch_result_text, self._("downloading_posts", username, 12))
                _, output = self.capture_output(lambda: self.stalker.download_recent_posts(username))
                
                # Çıktıyı ekrana yazdır
                for line in output.split('\n'):
                    if line.strip():
                        self.update_result_text(self.batch_result_text, line)
                
                # Başarı durumunu kontrol et
                if "not found" in output or "error" in output.lower():
                    success = False
            
            if success:
                self.update_result_text(self.batch_result_text, self._("batch_download_complete"))
                
        except Exception as e:
            self.update_result_text(self.batch_result_text, self._("batch_download_error", str(e)))
    
    def show_downloads(self):
        """İndirilen dosyaları göster."""
        # Sonuç dialog'unu göster
        dialog = tk.Toplevel(self)
        dialog.title("İndirilen Dosyalar")
        dialog.geometry("500x400")
        dialog.transient(self)  # Ana pencereye bağlı
        
        # Indirilenler alanı
        result_text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
        result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Çıktıyı yakalamak için işlevi çağır
        result, output = self.capture_output(lambda: self.stalker.list_downloads())
        
        # Çıktıyı ekrana yazdır
        result_text.insert(tk.END, output)
        result_text.config(state=tk.DISABLED)
        
        # Klasörü aç butonu
        open_button = ttk.Button(dialog, text="İndirilenler Klasörünü Aç", 
                                command=lambda: os.startfile(self.stalker.base_dir) if os.name == 'nt' 
                                else webbrowser.open('file://' + os.path.realpath(self.stalker.base_dir)))
        open_button.pack(side=tk.BOTTOM, pady=10)
        
        # Dialog'u ortala
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def clean_downloads(self):
        """Tüm indirilen dosyaları temizle."""
        confirm = messagebox.askyesno("Onay", "Tüm indirilen dosyalar silinecek. Emin misiniz?")
        
        if confirm:
            # Dosyaları temizle
            import shutil
            shutil.rmtree(self.stalker.base_dir, ignore_errors=True)
            self.stalker.base_dir.mkdir(exist_ok=True)
            for dir_path in self.stalker.content_types.values():
                dir_path.mkdir(exist_ok=True)
            
            self.update_status(self._("clean_success"))
            messagebox.showinfo("Başarılı", "Tüm indirilen dosyalar temizlendi!")
    
    def show_about(self):
        """Hakkında dialog'unu göster."""
        about_message = """
        📲 InstaStalker - Instagram İçerik İndirme Aracı
        
        Bu uygulama, Instagram hikayelerini, gönderilerini ve profil resimlerini
        indirmenizi sağlayan kullanıcı dostu bir araçtır.
        
        © 2023 - InstaStalker Ekibi
        """
        
        messagebox.showinfo("Hakkında", about_message)
    
    def change_language(self, event=None):
        """Dil değiştir."""
        # Yeni dili ayarla
        self.stalker.settings["language"] = self.lang_var.get()
        self.stalker.save_settings()
        
        # Pencere başlığını güncelle
        self.title(self._("app_title"))
        
        # Dil değişikliği olayını tetikle
        self.event_generate("<<LanguageChanged>>")
        
        # Durum çubuğunu güncelle
        self.update_status(self._("lang_changed", self.stalker.settings["language"]))
    
    def refresh_language(self, event=None):
        """Dil değişikliğinde UI metinlerini güncelle."""
        # Tab başlıkları
        self.tab_control.tab(0, text=self._("tab_stories") if "tab_stories" in TRANSLATIONS[self.lang_var.get()] else "Hikayeler")
        self.tab_control.tab(1, text=self._("tab_posts") if "tab_posts" in TRANSLATIONS[self.lang_var.get()] else "Gönderiler")
        self.tab_control.tab(2, text=self._("tab_profile") if "tab_profile" in TRANSLATIONS[self.lang_var.get()] else "Profil Resmi")
        self.tab_control.tab(3, text=self._("tab_batch") if "tab_batch" in TRANSLATIONS[self.lang_var.get()] else "Toplu İndirme")
        self.tab_control.tab(4, text=self._("tab_highlights") if "tab_highlights" in TRANSLATIONS[self.lang_var.get()] else "Öne Çıkanlar")
        self.tab_control.tab(5, text=self._("tab_log") if "tab_log" in TRANSLATIONS[self.lang_var.get()] else "Log")
    
    def on_close(self):
        """Uygulama kapatılırken yapılacak işlemler."""
        # Ayarları kaydet
        self.stalker.save_settings()
        
        # Uygulamayı kapat
        self.destroy()

    def fetch_highlights(self):
        """Öne çıkan hikayeleri getir."""
        username = self.highlights_username_var.get().strip()
        if not username:
            messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin.")
            return
        
        # Listbox'ı temizle
        self.highlights_listbox.delete(0, tk.END)
        self.highlights_result_text.config(state=tk.NORMAL)
        self.highlights_result_text.delete(1.0, tk.END)
        self.highlights_result_text.config(state=tk.DISABLED)
        
        # Butonları devre dışı bırak
        self.download_selected_button.config(state=tk.DISABLED)
        self.download_all_button.config(state=tk.DISABLED)
        
        # Öne çıkan hikayeleri getir
        threading.Thread(target=self._fetch_highlights_thread, args=(username,)).start()
    
    def _fetch_highlights_thread(self, username):
        """Arka planda öne çıkan hikayeleri getir."""
        try:
            self.update_status(f"{username} kullanıcısının öne çıkan hikayeleri getiriliyor...")
            self.update_result_text(self.highlights_result_text, f"⏳ {username} kullanıcısının öne çıkan hikayeleri getiriliyor...\n")
            
            # Cookies kontrolü
            if not self.stalker.cookies:
                self.update_result_text(self.highlights_result_text, "❌ Çerezler ayarlanmamış. Lütfen önce çerezleri ayarlayın.\n")
                messagebox.showerror("Hata", "Çerezler ayarlanmamış. Lütfen önce çerezleri ayarlayın.")
                return
            
            # Instagram'dan kullanıcının profil sayfasını çek
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(f"https://www.instagram.com/{username}/", headers=headers, cookies=self.stalker.cookies)
            
            if response.status_code != 200:
                self.update_result_text(self.highlights_result_text, f"❌ {username} kullanıcısının profili bulunamadı.\n")
                return
            
            # Kullanıcı ID'sini bulacak birden fazla regex dene
            user_id = None
            
            # Pattern 1: Orijinal pattern '"user_id":"(\d+)"'
            user_id_match = re.search(r'"user_id":"(\d+)"', response.text)
            if user_id_match:
                user_id = user_id_match.group(1)
            
            # Pattern 2: JSON formatında olabilir: "id":"12345678"
            if not user_id:
                user_id_match = re.search(r'"id":"(\d+)"[^}]*?"username":"{}"'.format(username), response.text)
                if user_id_match:
                    user_id = user_id_match.group(1)
            
            # Pattern 3: Farklı bir pattern 'profilePage_(\d+)'
            if not user_id:
                user_id_match = re.search(r'profilePage_(\d+)', response.text)
                if user_id_match:
                    user_id = user_id_match.group(1)
            
            # Pattern 4: Daha spesifik bir XPath tarzı sorgu
            if not user_id:
                user_id_match = re.search(r'"X-IG-App-ID":"[^"]+","user_id":"(\d+)"', response.text)
                if user_id_match:
                    user_id = user_id_match.group(1)
                    
            # Pattern 5: Instagram script tag'inden userId çıkarma
            if not user_id:
                user_id_match = re.search(r'<script[^>]*>\s*window\._sharedData\s*=\s*({.*?});</script>', response.text, re.DOTALL)
                if user_id_match:
                    try:
                        shared_data = json.loads(user_id_match.group(1))
                        user_id = shared_data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {}).get('id')
                    except:
                        pass
                        
            # Hiçbir şekilde ID bulunamazsa alternatif yöntem dene - profil resminden ID çıkar
            if not user_id:
                profile_pic_match = re.search(r'profile_pic_url":"([^"]+)"', response.text)
                if profile_pic_match:
                    pic_url = profile_pic_match.group(1).replace('\\u0026', '&')
                    profile_id_match = re.search(r'/(\d+)_', pic_url)
                    if profile_id_match:
                        user_id = profile_id_match.group(1)
            
            if not user_id:
                # Daha agresif bir yöntem - sayfadaki tüm sayısal ID'leri tarayalım
                all_ids = re.findall(r'"id":"(\d+)"', response.text)
                common_ids = {}
                
                for id in all_ids:
                    if id in common_ids:
                        common_ids[id] += 1
                    else:
                        common_ids[id] = 1
                
                # En çok tekrar eden ID'yi kullan (muhtemelen kullanıcı ID'si)
                if common_ids:
                    user_id = max(common_ids.items(), key=lambda x: x[1])[0]
            
            if not user_id:
                self.update_result_text(self.highlights_result_text, f"❌ {username} kullanıcısının ID'si bulunamadı.\n")
                self.update_result_text(self.highlights_result_text, "🔍 Instagram'ın yaptığı güncellemeler nedeniyle kullanıcı ID'si çıkarılamıyor.\n")
                self.update_result_text(self.highlights_result_text, "💡 Tarayıcınızda Web Geliştirici Araçlarını açıp, Network sekmesinde 'graphql' isminde bir istek bulabilir ve sorgu parametrelerinden user_id'yi manuel olarak bulabilirsiniz.\n")
                return
            
            self.update_result_text(self.highlights_result_text, f"✅ Kullanıcı ID'si bulundu: {user_id}\n")
            
            # Highlights API'sine istek gönder
            highlights_url = f"https://www.instagram.com/graphql/query/?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables=%7B%22user_id%22%3A%22{user_id}%22%2C%22include_chaining%22%3Afalse%2C%22include_reel%22%3Afalse%2C%22include_suggested_users%22%3Afalse%2C%22include_logged_out_extras%22%3Afalse%2C%22include_highlight_reels%22%3Atrue%2C%22include_related_profiles%22%3Afalse%7D"
            
            highlights_response = requests.get(highlights_url, headers=headers, cookies=self.stalker.cookies)
            
            if highlights_response.status_code != 200:
                self.update_result_text(self.highlights_result_text, f"❌ {username} kullanıcısının öne çıkan hikayeleri alınamadı.\n")
                return
            
            # Highlights verilerini ayrıştır
            highlights_data = highlights_response.json()
            highlights = highlights_data.get('data', {}).get('user', {}).get('edge_highlight_reels', {}).get('edges', [])
            
            if not highlights:
                self.update_result_text(self.highlights_result_text, f"ℹ️ {username} kullanıcısının öne çıkan hikayesi bulunamadı.\n")
                return
            
            # Öne çıkan hikayeleri listele
            self.update_result_text(self.highlights_result_text, f"✅ {username} kullanıcısının {len(highlights)} adet öne çıkan hikayesi bulundu.\n")
            
            # Highlight bilgilerini sakla
            self.current_highlights = []
            
            # Highlights listesini doldur
            for i, highlight in enumerate(highlights):
                node = highlight.get('node', {})
                title = node.get('title', f"Highlight-{i+1}")
                highlight_id = node.get('id')
                media_count = node.get('highlight_reel_count', 0)
                
                self.current_highlights.append({
                    'title': title,
                    'id': highlight_id,
                    'count': media_count
                })
                
                self.highlights_listbox.insert(tk.END, f"{title} ({media_count} hikaye)")
            
            # Butonları etkinleştir
            self.download_selected_button.config(state=tk.NORMAL)
            self.download_all_button.config(state=tk.NORMAL)
            
            self.update_status(f"{username} kullanıcısının öne çıkan hikayeleri listelendi")
            
        except Exception as e:
            self.update_result_text(self.highlights_result_text, f"❌ Hata: {str(e)}\n")
            messagebox.showerror("Hata", f"Öne çıkan hikayeler alınırken bir hata oluştu: {str(e)}")
    
    def download_selected_highlight(self):
        """Seçilen öne çıkan hikayeyi indir."""
        selected_idx = self.highlights_listbox.curselection()
        if not selected_idx:
            messagebox.showerror("Hata", "Lütfen indirmek istediğiniz bir öne çıkan hikaye seçin.")
            return
        
        idx = selected_idx[0]
        if idx < 0 or idx >= len(self.current_highlights):
            return
        
        highlight = self.current_highlights[idx]
        username = self.highlights_username_var.get().strip()
        
        threading.Thread(target=self._download_highlight_thread, args=(username, highlight)).start()
    
    def download_all_highlights(self):
        """Tüm öne çıkan hikayeleri indir."""
        if not self.current_highlights:
            return
        
        username = self.highlights_username_var.get().strip()
        threading.Thread(target=self._download_all_highlights_thread, args=(username, self.current_highlights)).start()
    
    def _download_highlight_thread(self, username, highlight):
        """Arka planda bir öne çıkan hikayeyi indir."""
        try:
            title = highlight['title']
            self.update_status(f"'{title}' öne çıkan hikayesi indiriliyor...")
            self.update_result_text(self.highlights_result_text, f"\n⏳ '{title}' öne çıkan hikayesi indiriliyor...\n")
            
            # Öne çıkan hikayeyi indir
            base_dir = self.stalker.content_types["stories"] / username / "highlights"
            success = self.stalker._download_single_highlight(username, highlight, base_dir)
            
            if success:
                self.update_status(f"'{title}' öne çıkan hikayesi başarıyla indirildi")
            else:
                self.update_status(f"'{title}' öne çıkan hikayesi indirilirken bir hata oluştu")
                
        except Exception as e:
            self.update_result_text(self.highlights_result_text, f"❌ Hata: {str(e)}\n")
            messagebox.showerror("Hata", f"Öne çıkan hikaye indirilirken bir hata oluştu: {str(e)}")
    
    def _download_all_highlights_thread(self, username, highlights):
        """Arka planda tüm öne çıkan hikayeleri indir."""
        try:
            self.update_status(f"{username} kullanıcısının tüm öne çıkan hikayeleri indiriliyor...")
            self.update_result_text(self.highlights_result_text, f"\n⏳ {len(highlights)} adet öne çıkan hikaye indiriliyor...\n")
            
            base_dir = self.stalker.content_types["stories"] / username / "highlights"
            base_dir.mkdir(exist_ok=True, parents=True)
            
            success_count = 0
            fail_count = 0
            
            for i, highlight in enumerate(highlights, 1):
                title = highlight['title']
                self.update_result_text(self.highlights_result_text, f"⏳ [{i}/{len(highlights)}] '{title}' öne çıkan hikayesi indiriliyor...\n")
                
                try:
                    success = self.stalker._download_single_highlight(username, highlight, base_dir)
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        self.update_result_text(self.highlights_result_text, f"❌ '{title}' öne çıkan hikayesi indirilemedi\n")
                except Exception as e:
                    fail_count += 1
                    self.update_result_text(self.highlights_result_text, f"❌ '{title}' indirilirken hata: {str(e)}\n")
            
            summary = f"\n✅ Toplam {len(highlights)} öne çıkan hikayeden {success_count} tanesi başarıyla indirildi"
            if fail_count > 0:
                summary += f", {fail_count} tanesi başarısız oldu"
                
            self.update_result_text(self.highlights_result_text, summary + "\n")
            self.update_status(f"{username} kullanıcısının öne çıkan hikayeleri indirildi ({success_count}/{len(highlights)})")
            
        except Exception as e:
            self.update_result_text(self.highlights_result_text, f"❌ Hata: {str(e)}\n")
            messagebox.showerror("Hata", f"Öne çıkan hikayeler indirilirken bir hata oluştu: {str(e)}")


def main():
    """Ana fonksiyon - GUI uygulamasını başlat."""
    app = InstaStalkGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
    