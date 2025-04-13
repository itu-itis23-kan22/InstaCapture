#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from pathlib import Path
import json
import webbrowser
import re
from datetime import datetime

# Paket yükleme fonksiyonu
def install_package(package_name):
    """Belirtilen paketi pip ile yüklemeyi dener"""
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
        except subprocess.CalledProcessError as e:
            print(f"Komut başarısız oldu: {' '.join(cmd)}, hata kodu: {e.returncode}")
            continue
        except FileNotFoundError as e:
            print(f"Komut bulunamadı: {cmd[0]}")
            continue
    
    return False

# Gerekli paketleri yüklemeyi dene
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
except ImportError as e:
    print(f"Tkinter paketi bulunamadı: {e}")
    print("Tkinter, Python kurulumunuzla gelmelidir. Lütfen Python'u Tkinter desteğiyle yeniden kurun.")
    sys.exit(1)

# threading standart kütüphane olduğu için kontrol etmeye gerek yok
import threading

# Diğer paketleri kontrol et ve yüklemeyi dene
required_packages = []

# PIL modülü
try:
    from PIL import Image, ImageTk
except ImportError:
    required_packages.append("pillow")
    
# Requests modülü  
try:
    import requests
except ImportError:
    required_packages.append("requests")

# Eksik paketleri yüklemeyi dene
if required_packages:
    print(f"Eksik paketler bulundu: {', '.join(required_packages)}")
    print("Paketler otomatik olarak yüklenmeye çalışılacak...")
    
    success = True
    for package in required_packages:
        if not install_package(package):
            success = False
            print(f"{package} paketi yüklenemedi.")
    
    if not success:
        print("\nBazı paketler yüklenemedi.")
        print("Lütfen manuel olarak şu komutu çalıştırın:")
        print(f"pip install {' '.join(required_packages)}")
        print("\nVeya şunları deneyebilirsiniz:")
        print(f"{sys.executable} -m pip install {' '.join(required_packages)}")
        sys.exit(1)
    
    print("Paketler yüklendi, modüller içe aktarılıyor...")
    
    # Yeniden import etmeyi dene
    try:
        if "pillow" in required_packages:
            from PIL import Image, ImageTk
        if "requests" in required_packages:
            import requests
    except ImportError as e:
        print(f"Paketler yüklendikten sonra bile import hatası: {e}")
        print("Lütfen uygulamayı yeniden başlatın veya gerekli paketleri manuel olarak yükleyin.")
        sys.exit(1)

# InstaStalk sınıfını içe aktar
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
try:
    from instastalk import InstaStalker, TRANSLATIONS
except ImportError as e:
    print(f"instastalk.py dosyası bulunamadı veya içe aktarılamadı: {e}")
    print("Lütfen instastalk.py dosyasının bu script ile aynı klasörde olduğundan emin olun.")
    sys.exit(1)

# Thread güvenli GUI güncellemeleri için yardımcı fonksiyonlar
def is_main_thread():
    return threading.current_thread() is threading.main_thread()

class InstaStalkGUI(tk.Tk):
    """InstaStalker için grafik arayüz."""
    
    def __init__(self):
        super().__init__()
        
        # Ana uygulama nesnesi oluştur
        self.stalker = InstaStalker()
        
        # Current text widget for update_result_text
        self.current_text_widget = None
        
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
        self.username_entry = ttk.Entry(username_frame, textvariable=self.story_username_var, width=30)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        # İndirme butonu
        download_button = ttk.Button(username_frame, text="Hikayeleri İndir", command=self.download_stories)
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
        download_button = ttk.Button(url_frame, text="Gönderiyi İndir", command=self.download_posts)
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
    
    def update_result_text(self, text, append=True, clear_first=False):
        """Thread-safe way to update result text widget"""
        if self.current_text_widget is None:
            print("WARNING: current_text_widget is not set. Using the first tab's text widget.")
            # Default to story_result_text if not set
            self.current_text_widget = self.story_result_text
            
        def _update():
            if clear_first:
                self.current_text_widget.config(state=tk.NORMAL)
                self.current_text_widget.delete(1.0, tk.END)
                self.current_text_widget.config(state=tk.DISABLED)
                
            self.current_text_widget.config(state=tk.NORMAL)
            if append:
                current_text = self.current_text_widget.get(1.0, tk.END)
                if current_text and not current_text.strip() == "":
                    self.current_text_widget.insert(tk.END, f"\n{text}")
                else:
                    self.current_text_widget.insert(tk.END, text)
            else:
                self.current_text_widget.delete(1.0, tk.END)
                self.current_text_widget.insert(tk.END, text)
            
            # Auto-scroll to the end
            self.current_text_widget.see(tk.END)
            self.current_text_widget.config(state=tk.DISABLED)
        
        if is_main_thread():
            _update()
        else:
            self.after(0, _update)
    
    def update_result_text_widget(self, widget, text, append=True):
        """Thread-safe way to update any text widget"""
        def _update():
            widget.config(state=tk.NORMAL)
            
            if append:
                current_text = widget.get(1.0, tk.END)
                if current_text and not current_text.strip() == "":
                    widget.insert(tk.END, f"\n{text}")
                else:
                    widget.insert(tk.END, text)
            else:
                widget.delete(1.0, tk.END)
                widget.insert(tk.END, text)
            
            # Auto-scroll to the end
            widget.see(tk.END)
            widget.config(state=tk.DISABLED)
        
        if is_main_thread():
            _update()
        else:
            self.after(0, _update)
    
    def update_status(self, text):
        """Thread-safe way to update status label"""
        def _update():
            self.status_var.set(text)
            self.update_idletasks()
        
        if is_main_thread():
            _update()
        else:
            self.after(0, _update)
            
    def download_stories(self):
        """Download stories of given username"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror(self._("error"), self._("enter_username"))
            return
        
        # Set current text widget
        self.current_text_widget = self.story_result_text
        
        # Clear previous results and update status
        self.update_result_text_widget(self.story_result_text, "", append=False)
        self.update_status(f"{self._('downloading_stories')} {username}...")
        
        # Start download in a separate thread
        download_thread = threading.Thread(target=self._download_stories_thread, args=(username,))
        download_thread.daemon = True
        download_thread.start()
    
    def _download_stories_thread(self, username):
        """Background thread for downloading stories"""
        try:
            # Check for cookies
            cookies = self.stalker.get_cookies_dict()
            if not cookies:
                self.update_status(self._("cookies_required"))
                self.update_result_text_widget(self.current_text_widget, f"⚠️ {self._('cookies_required_explanation')}")
                return
            
            # Get the user ID
            user_id = self._get_user_id_from_profile(username)
            
            if not user_id:
                self.update_status(self._("user_id_not_found"))
                self.update_result_text_widget(self.current_text_widget, f"❌ {self._('could_not_find_user_id').format(username=username)}")
                return
                
            # Fetch stories
            self.update_status(f"{self._('fetching_stories')} {username} (ID: {user_id})...")
            
            start_time = time.time()
            
            try:
                # Create directory for saving if it doesn't exist
                save_dir = os.path.join("instagram_content", "stories", username)
                os.makedirs(save_dir, exist_ok=True)
                
                story_response = self.stalker.get_stories(user_id)
                
                # Check if there are any stories
                if not story_response.get("reels_media"):
                    self.update_status(f"{self._('no_stories')} {username}")
                    self.update_result_text_widget(self.current_text_widget, f"ℹ️ {self._('no_active_stories').format(username=username)}")
                    return
                
                stories = story_response["reels_media"][0]["items"]
                story_count = len(stories)
                
                self.update_status(f"{self._('found_stories').format(count=story_count, username=username)}")
                self.update_result_text_widget(self.current_text_widget, f"🔍 {self._('found_stories').format(count=story_count, username=username)}")
                
                # Download each story
                for i, story in enumerate(stories, 1):
                    self.update_status(f"{self._('downloading_story')} {i}/{story_count}...")
                    
                    # Determine if it's a photo or video
                    if "video_versions" in story:
                        # It's a video
                        video_url = story["video_versions"][0]["url"]
                        timestamp = story.get("taken_at", int(time.time()))
                        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H-%M-%S")
                        filename = f"{date_str}_video.mp4"
                        file_path = os.path.join(save_dir, filename)
                        
                        # Download the video
                        with requests.get(video_url, stream=True, timeout=(10, 30)) as r:
                            r.raise_for_status()
                            with open(file_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        
                        media_type = self._("video")
                    else:
                        # It's an image
                        image_url = story["image_versions2"]["candidates"][0]["url"]
                        timestamp = story.get("taken_at", int(time.time()))
                        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H-%M-%S")
                        filename = f"{date_str}_image.jpg"
                        file_path = os.path.join(save_dir, filename)
                        
                        # Download the image
                        with requests.get(image_url, timeout=(10, 30)) as r:
                            r.raise_for_status()
                            with open(file_path, 'wb') as f:
                                f.write(r.content)
                        
                        media_type = self._("image")
                    
                    self.update_result_text_widget(self.current_text_widget, f"✅ {self._('downloaded_story').format(number=i, type=media_type)}")
                
                elapsed_time = time.time() - start_time
                self.update_status(f"{self._('download_complete')} ({story_count} {self._('stories')} - {elapsed_time:.1f}s)")
                self.update_result_text_widget(self.current_text_widget, f"\n📁 {self._('saved_in').format(path=save_dir)}")
                
            except requests.RequestException as e:
                self.update_status(f"{self._('network_error')}: {e}")
                self.update_result_text_widget(self.current_text_widget, f"❌ {self._('network_error')}: {e}")
            except json.JSONDecodeError:
                self.update_status(self._("invalid_response"))
                self.update_result_text_widget(self.current_text_widget, f"❌ {self._('invalid_response_explanation')}")
            except KeyError as e:
                self.update_status(f"{self._('format_error')}: {e}")
                self.update_result_text_widget(self.current_text_widget, f"❌ {self._('format_error_explanation')}")
                
        except Exception as e:
            self.update_status(f"{self._('error')}: {e}")
            self.update_result_text_widget(self.current_text_widget, f"❌ {self._('unexpected_error')}: {str(e)}")
            # Log more detailed error information for debugging
            import traceback
            print(f"Error in download_stories: {traceback.format_exc()}")
    
    def download_posts(self):
        """Download posts of given username"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror(self._("error"), self._("enter_username"))
            return
        
        limit = simpledialog.askinteger(
            self._("post_limit"), 
            self._("post_limit_prompt"),
            initialvalue=5,
            minvalue=1,
            maxvalue=50
        )
        
        if limit is None:
            return  # User cancelled the dialog
        
        # Set current text widget
        self.current_text_widget = self.post_result_text
        
        # Clear previous results and update status
        self.update_result_text_widget(self.post_result_text, "", append=False)
        self.update_status(f"{self._('downloading_posts')} {username} ({limit} posts)...")
        
        # Start download in a separate thread
        download_thread = threading.Thread(target=self._download_posts_thread, args=(username, limit))
        download_thread.daemon = True
        download_thread.start()
        
    def _download_posts_thread(self, username, limit):
        """Background thread for downloading posts"""
        try:
            # Check for cookies
            cookies = self.stalker.get_cookies_dict()
            if not cookies:
                self.update_status(self._("cookies_required"))
                self.update_result_text_widget(self.current_text_widget, f"⚠️ {self._('cookies_required_explanation')}")
                return
                
            # Get the user ID (optional for posts but useful for better queries)
            user_id = self._get_user_id_from_profile(username)
            
            start_time = time.time()
            
            try:
                # Create directory for saving if it doesn't exist
                save_dir = os.path.join("instagram_content", "posts", username)
                os.makedirs(save_dir, exist_ok=True)
                
                # Fetch and download posts
                posts = self.stalker.get_posts(username, limit)
                
                if not posts:
                    self.update_status(f"{self._('no_posts')} {username}")
                    self.update_result_text_widget(self.current_text_widget, f"ℹ️ {self._('no_posts_found').format(username=username)}")
                    return
                
                post_count = len(posts)
                self.update_status(f"{self._('found_posts').format(count=post_count, username=username)}")
                self.update_result_text_widget(self.current_text_widget, f"🔍 {self._('found_posts').format(count=post_count, username=username)}")
                
                # Track downloaded media count
                total_media = 0
                
                # Download each post
                for i, post in enumerate(posts, 1):
                    self.update_status(f"{self._('downloading_post')} {i}/{post_count}...")
                    
                    # Get post timestamp for filename
                    timestamp = post.get("taken_at", int(time.time()))
                    date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d_%H-%M-%S")
                    
                    # Handle carousel posts
                    if post.get("carousel_media"):
                        # Multiple images/videos in one post
                        for j, media in enumerate(post["carousel_media"], 1):
                            if media.get("video_versions"):
                                # Download video from carousel
                                video_url = media["video_versions"][0]["url"]
                                filename = f"{date_str}_carousel_{j}_video.mp4"
                                file_path = os.path.join(save_dir, filename)
                                
                                with requests.get(video_url, stream=True, timeout=(10, 30)) as r:
                                    r.raise_for_status()
                                    with open(file_path, 'wb') as f:
                                        for chunk in r.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                
                                media_type = self._("video")
                            else:
                                # Download image from carousel
                                image_url = media["image_versions2"]["candidates"][0]["url"]
                                filename = f"{date_str}_carousel_{j}_image.jpg"
                                file_path = os.path.join(save_dir, filename)
                                
                                with requests.get(image_url, timeout=(10, 30)) as r:
                                    r.raise_for_status()
                                    with open(file_path, 'wb') as f:
                                        f.write(r.content)
                                
                                media_type = self._("image")
                            
                            total_media += 1
                            self.update_result_text_widget(self.current_text_widget, f"✅ {self._('downloaded_carousel_item').format(post=i, item=j, type=media_type)}")
                    
                    elif post.get("video_versions"):
                        # Single video post
                        video_url = post["video_versions"][0]["url"]
                        filename = f"{date_str}_video.mp4"
                        file_path = os.path.join(save_dir, filename)
                        
                        with requests.get(video_url, stream=True, timeout=(10, 30)) as r:
                            r.raise_for_status()
                            with open(file_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        
                        total_media += 1
                        self.update_result_text_widget(self.current_text_widget, f"✅ {self._('downloaded_post').format(number=i, type=self._('video'))}")
                    
                    else:
                        # Single image post
                        image_url = post["image_versions2"]["candidates"][0]["url"]
                        filename = f"{date_str}_image.jpg"
                        file_path = os.path.join(save_dir, filename)
                        
                        with requests.get(image_url, timeout=(10, 30)) as r:
                            r.raise_for_status()
                            with open(file_path, 'wb') as f:
                                f.write(r.content)
                        
                        total_media += 1
                        self.update_result_text_widget(self.current_text_widget, f"✅ {self._('downloaded_post').format(number=i, type=self._('image'))}")
                
                elapsed_time = time.time() - start_time
                self.update_status(f"{self._('download_complete')} ({total_media} {self._('media')} - {elapsed_time:.1f}s)")
                self.update_result_text_widget(self.current_text_widget, f"\n📁 {self._('saved_in').format(path=save_dir)}")
                
            except requests.RequestException as e:
                self.update_status(f"{self._('network_error')}: {e}")
                self.update_result_text_widget(self.current_text_widget, f"❌ {self._('network_error')}: {e}")
            except json.JSONDecodeError:
                self.update_status(self._("invalid_response"))
                self.update_result_text_widget(self.current_text_widget, f"❌ {self._('invalid_response_explanation')}")
            except KeyError as e:
                self.update_status(f"{self._('format_error')}: {e}")
                self.update_result_text_widget(self.current_text_widget, f"❌ {self._('format_error_explanation')}")
                
        except Exception as e:
            self.update_status(f"{self._('error')}: {e}")
            self.update_result_text_widget(self.current_text_widget, f"❌ {self._('unexpected_error')}: {str(e)}")
            # Log more detailed error information for debugging
            import traceback
            print(f"Error in download_posts: {traceback.format_exc()}")
    
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
            self.update_result_text(self._("batch_download_start", username))
            
            success = True
            
            # Hikayeleri indir
            if choice in ["1", "3"]:
                self.update_result_text(self._("downloading_stories", username))
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
                self.update_result_text(self._("downloading_posts", username, 12))
                _, output = self.capture_output(lambda: self.stalker.download_recent_posts(username))
                
                # Çıktıyı ekrana yazdır
                for line in output.split('\n'):
                    if line.strip():
                        self.update_result_text(self.batch_result_text, line)
                
                # Başarı durumunu kontrol et
                if "not found" in output or "error" in output.lower():
                    success = False
            
            if success:
                self.update_result_text(self._("batch_download_complete"))
                
        except Exception as e:
            self.update_result_text(self._("batch_download_error", str(e)))
    
    def show_downloads(self):
        """Show downloads folder in file explorer in a platform-independent way"""
        download_dir = os.path.abspath("instagram_content")
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        
        # Open file explorer in a platform-independent way
        try:
            if sys.platform == "win32":
                os.startfile(download_dir)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", download_dir], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", download_dir], check=True)
            
            self.update_status(f"{self._('opened_folder')}: {download_dir}")
        except Exception as e:
            self.update_status(f"{self._('error_opening_folder')}: {e}")
            self.update_result_text(f"📁 {self._('downloads_located_at')}: {download_dir}")
    
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
        
    def show_cookies_dialog(self):
        """Instagram çerezlerini ayarlamak için dialog göster"""
        # Kullanıcıya açıklama mesajı göster
        instructions = (
            "Instagram çerezlerini ayarlamak için:\n\n"
            "1. Tarayıcıda Instagram.com'a giriş yapın\n"
            "2. Geliştirici Araçlarını açın (F12 veya Ctrl+Shift+I)\n"
            "3. Network sekmesine gidin\n"
            "4. Instagram.com'u yenileyin\n"
            "5. Herhangi bir isteği seçin\n"
            "6. Headers (Başlıklar) tabını seçin\n"
            "7. Request Headers bölümünde 'cookie' değerini bulun\n"
            "8. Cookie değerinin tamamını kopyalayın\n\n"
            "Cookie değeri şuna benzer olmalıdır:\n"
            "mid=...; ig_did=...; ds_user_id=...; sessionid=...; csrftoken=..."
        )
        
        # Çerez değerini girmesi için kullanıcıya sor
        cookie_str = simpledialog.askstring("Instagram Çerezlerini Ayarla", 
                                          instructions, 
                                          parent=self)
        
        if cookie_str and cookie_str.strip():
            # Çerezleri ayarla
            success = self.stalker.set_cookies_from_string(cookie_str.strip())
            
            if success:
                messagebox.showinfo("Başarılı", f"Çerezler başarıyla kaydedildi: {self.stalker.cookies_file}")
                self.update_status(f"Çerezler kaydedildi: {self.stalker.cookies_file}")
            else:
                messagebox.showerror("Hata", "Çerezler kaydedilirken bir hata oluştu!")

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
        try:
            self.update_status(f"{username} kullanıcısının öne çıkan hikayeleri getiriliyor...")
            self.update_result_text_widget(self.highlights_result_text, f"⏳ {username} kullanıcısının öne çıkan hikayeleri getiriliyor...\n")
            
            # Cookies kontrolü
            if not self.stalker.cookies:
                self.update_result_text_widget(self.highlights_result_text, "❌ Çerezler ayarlanmamış. Lütfen önce çerezleri ayarlayın.\n")
                messagebox.showerror("Hata", "Çerezler ayarlanmamış. Lütfen önce çerezleri ayarlayın.")
                return
            
            # Instagram'dan kullanıcının profil sayfasını çek
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(f"https://www.instagram.com/{username}/", headers=headers, cookies=self.stalker.cookies)
            
            if response.status_code != 200:
                self.update_result_text_widget(self.highlights_result_text, f"❌ {username} kullanıcısının profili bulunamadı.\n")
                return
            
            # Kullanıcı ID'sini bulacak birden fazla regex dene
            user_id = None
            
            # Pattern 1: Orijinal pattern '"user_id":"(\d+)"'
            user_id_match = re.search(r'"user_id":"(\d+)"', response.text)
            if user_id_match:
                user_id = user_id_match.group(1)
            
            # Pattern 2: JSON formatında olabilir: "id":"12345678"
            if not user_id:
                # Süslü parantezleri formatlamada kullanırken escape etmek için ikiye katlıyoruz
                pattern = r'"id":"(\d+)"[^}]*?"username":"' + re.escape(username) + r'"'
                user_id_match = re.search(pattern, response.text)
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
                if common_ids and len(common_ids) > 0:
                    user_id = max(common_ids.items(), key=lambda x: x[1])[0]
            
            if not user_id:
                self.update_result_text_widget(self.highlights_result_text, f"❌ {username} kullanıcısının ID'si bulunamadı.\n")
                self.update_result_text_widget(self.highlights_result_text, "🔍 Instagram'ın yaptığı güncellemeler nedeniyle kullanıcı ID'si çıkarılamıyor.\n")
                
                # Kullanıcıdan manual ID girme seçeneği sun
                self.update_result_text_widget(self.highlights_result_text, "💡 Kullanıcı ID'sini manuel olarak girebilirsiniz.\n")
                
                # Manuel ID girmek için dialog oluştur
                manual_id = simpledialog.askstring("Kullanıcı ID'sini Girin", 
                                                 f"{username} kullanıcısının ID'sini manuel olarak girin.\n\n"
                                                 "ID'yi bulmak için:\n"
                                                 "1. Tarayıcıda Instagram'a gidin\n"
                                                 "2. Web Geliştirici Araçlarını açın (F12)\n"
                                                 "3. Network sekmesine tıklayın\n"
                                                 "4. Sayfayı yenileyin\n"
                                                 "5. 'graphql' içeren bir isteği bulun\n"
                                                 "6. Sorgu parametrelerinde 'user_id' değerini arayın")
                
                if manual_id and manual_id.strip() and manual_id.isdigit():
                    user_id = manual_id.strip()
                    self.update_result_text_widget(self.highlights_result_text, f"✅ Manuel olarak girilen ID kullanılıyor: {user_id}\n")
                else:
                    self.update_result_text_widget(self.highlights_result_text, "❌ Geçerli bir kullanıcı ID'si girilmedi. İşlem iptal edildi.\n")
                    return
            
            self.update_result_text_widget(self.highlights_result_text, f"✅ Kullanıcı ID'si bulundu: {user_id}\n")
            
            # Highlights API'sine istek gönder
            # Güncel query_hash değeri kullanılıyor
            highlights_url = f"https://www.instagram.com/graphql/query/?query_hash=d4d88dc1500312af6f937f7b804c68c3&variables=%7B%22user_id%22%3A%22{user_id}%22%2C%22include_chaining%22%3Afalse%2C%22include_reel%22%3Afalse%2C%22include_suggested_users%22%3Afalse%2C%22include_logged_out_extras%22%3Afalse%2C%22include_highlight_reels%22%3Atrue%2C%22include_live_status%22%3Atrue%7D"
            
            highlights_response = requests.get(highlights_url, headers=headers, cookies=self.stalker.cookies)
            
            if highlights_response.status_code != 200:
                self.update_result_text_widget(self.highlights_result_text, f"❌ {username} kullanıcısının öne çıkan hikayeleri alınamadı.\n")
                return
            
            # Highlights verilerini ayrıştır
            try:
                highlights_data = highlights_response.json()
                if not highlights_data:
                    self.update_result_text_widget(self.highlights_result_text, f"❌ {username} kullanıcısının öne çıkan hikayeleri için geçerli veri alınamadı.\n")
                    return
                
                # Yanıt yapısını inceleme
                self.update_result_text_widget(self.highlights_result_text, f"ℹ️ API yanıtı inceleniyor...\n")
                
                # Yanıt yapısını kontrol et ve farklı formatları dene
                highlights = None
                
                # Otomatik olarak yanıt yapısını tespit etmeye çalış
                if 'data' in highlights_data:
                    data = highlights_data['data']
                    
                    # Olası yolları ara
                    if 'user' in data and data['user']:
                        user_data = data['user']
                        if 'edge_highlight_reels' in user_data:
                            edge_highlight_reels = user_data['edge_highlight_reels']
                            if 'edges' in edge_highlight_reels:
                                highlights = edge_highlight_reels['edges']
                                self.update_result_text_widget(self.highlights_result_text, "✅ Highlight verisi bulundu: data.user.edge_highlight_reels.edges yapısında\n")
                
                # Format 2: user.edge_highlight_reels.edges - eskiden kalan eski yöntem, yine de deneyelim
                if not highlights and 'user' in highlights_data and highlights_data.get('user'):
                    user = highlights_data.get('user')
                    if 'edge_highlight_reels' in user and user.get('edge_highlight_reels'):
                        edge_highlight_reels = user.get('edge_highlight_reels')
                        if 'edges' in edge_highlight_reels and edge_highlight_reels.get('edges'):
                            highlights = edge_highlight_reels.get('edges')
                
                # Format 3: edge_highlight_reels.edges - eskiden kalan eski yöntem, yine de deneyelim
                if not highlights and 'edge_highlight_reels' in highlights_data and highlights_data.get('edge_highlight_reels'):
                    edge_highlight_reels = highlights_data.get('edge_highlight_reels')
                    if 'edges' in edge_highlight_reels and edge_highlight_reels.get('edges'):
                        highlights = edge_highlight_reels.get('edges')
                
                # Format 4: data.edges - eskiden kalan eski yöntem, yine de deneyelim
                if not highlights and 'data' in highlights_data and highlights_data.get('data'):
                    data = highlights_data.get('data')
                    if 'edges' in data and data.get('edges'):
                        highlights = data.get('edges')
                
                # Hiçbir format bulunamadıysa hata ver
                if not highlights:
                    # API yanıtını detaylı incele ve rapor et
                    debug_str = f"❌ API yanıtında beklenen format bulunamadı.\nYanıt içeriği (ilk 1000 karakter):\n"
                    debug_str += json.dumps(highlights_data)[:1000] + "...\n"
                    debug_str += "API'nin üst seviye anahtarları: " + ", ".join(highlights_data.keys()) + "\n"
                    
                    if 'data' in highlights_data:
                        debug_str += "'data' anahtarının içindeki anahtarlar: " + ", ".join(highlights_data['data'].keys()) + "\n"
                    
                    self.update_result_text_widget(self.highlights_result_text, debug_str)
                    
                    # Kullanıcıya manuel olarak devam etme seçeneği sun
                    highlights_manual = simpledialog.askstring("Öne Çıkan Hikayeleri Manuel Bul", 
                                                              f"{username} kullanıcısının öne çıkan hikayeleri otomatik olarak bulunamadı.\n\n"
                                                              "Eğer API yanıt çıktısında istenen veri yapısını tespit ettiyseniz,\n"
                                                              "ilgili JSON yolunu nokta ile ayırarak girin (örn: 'data.user.edge_highlight_reels.edges'):")
                    
                    if highlights_manual:
                        try:
                            # Nokta notasyonu ile verilen yolu takip et
                            parts = highlights_manual.strip().split('.')
                            current = highlights_data
                            for part in parts:
                                if part.isdigit():
                                    # Sayısal indeks kullanılıyorsa listeye eriş
                                    current = current[int(part)]
                                else:
                                    current = current.get(part, {})
                            
                            if current and isinstance(current, list):
                                highlights = current
                                self.update_result_text_widget(self.highlights_result_text, f"✅ Manuel olarak belirtilen yoldan öne çıkan hikayeler bulundu.\n")
                            else:
                                self.update_result_text_widget(self.highlights_result_text, f"❌ Belirtilen yoldan geçerli bir liste bulunamadı.\n")
                                return
                        except Exception as e:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Manuel yol işlenirken hata: {str(e)}\n")
                            return
                    else:
                        self.update_result_text_widget(self.highlights_result_text, f"ℹ️ {username} kullanıcısının öne çıkan hikayesi bulunamadı.\n")
                        return
                
            except Exception as e:
                self.update_result_text_widget(self.highlights_result_text, f"❌ Highlights verisi ayrıştırılamadı: {str(e)}\n")
                error_details = f"Response status: {highlights_response.status_code}, Content: {highlights_response.text[:100]}..."
                self.update_result_text_widget(self.highlights_result_text, f"Hata detayları: {error_details}\n")
                return
            
            if not highlights:
                self.update_result_text_widget(self.highlights_result_text, f"ℹ️ {username} kullanıcısının öne çıkan hikayesi bulunamadı.\n")
                return
            
            # Öne çıkan hikayeleri listele
            self.update_result_text_widget(self.highlights_result_text, f"✅ {username} kullanıcısının {len(highlights)} adet öne çıkan hikayesi bulundu.\n")
            
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
            self.update_result_text_widget(self.highlights_result_text, f"❌ Hata: {str(e)}\n")
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
            highlight_id = highlight['id']
            self.update_status(f"'{title}' öne çıkan hikayesi indiriliyor...")
            self.update_result_text_widget(self.highlights_result_text, f"\n⏳ '{title}' öne çıkan hikayesi indiriliyor...\n")
            
            # Klasör oluştur
            try:
                base_dir = self.stalker.content_types["stories"] / username / "highlights"
                highlight_dir = base_dir / title.replace("/", "_").replace("\\", "_")
                highlight_dir.mkdir(exist_ok=True, parents=True)
            except PermissionError as e:
                self.update_result_text_widget(self.highlights_result_text, f"❌ Klasör oluşturma izin hatası: {str(e)}\n")
                return False
            except Exception as e:
                self.update_result_text_widget(self.highlights_result_text, f"❌ Klasör oluşturma hatası: {str(e)}\n")
                return False
            
            # Highlight içeriğini al
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Güncel API query_hash kullan
            highlight_url = f"https://www.instagram.com/graphql/query/?query_hash=45246d3fe16ccc6577e0bd297a5db1ab&variables=%7B%22reel_ids%22%3A%5B%22{highlight_id}%22%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%22{highlight_id}%22%5D%2C%22precomposed_overlay%22%3Afalse%7D"
            
            try:
                # Timeout ekle - 30 saniye bağlantı, 60 saniye okuma için
                highlight_response = requests.get(highlight_url, headers=headers, cookies=self.stalker.cookies, 
                                                timeout=(30, 60))
            except requests.exceptions.Timeout:
                self.update_result_text_widget(self.highlights_result_text, f"❌ API isteği zaman aşımına uğradı. Lütfen internet bağlantınızı kontrol edin.\n")
                return False
            except requests.exceptions.ConnectionError:
                self.update_result_text_widget(self.highlights_result_text, f"❌ Bağlantı hatası. Lütfen internet bağlantınızı kontrol edin.\n")
                return False
            except requests.exceptions.RequestException as e:
                self.update_result_text_widget(self.highlights_result_text, f"❌ API istek hatası: {str(e)}\n")
                return False
            
            if highlight_response.status_code != 200:
                self.update_result_text_widget(self.highlights_result_text, f"❌ Highlight içeriği alınamadı. HTTP Kodu: {highlight_response.status_code}\n")
                return False
            
            # Highlight verisini ayrıştır
            try:
                highlight_data = highlight_response.json()
                if not highlight_data:
                    self.update_result_text_widget(self.highlights_result_text, f"❌ Highlight verisi alınamadı veya boş.\n")
                    return False
                
                self.update_result_text_widget(self.highlights_result_text, f"ℹ️ Highlight medya verileri inceleniyor...\n")
                
                # Medya içeriğine erişim için farklı JSON yapılarını dene
                media_items = []
                
                # En yaygın format: data.reels_media[0].items
                if 'data' in highlight_data and 'reels_media' in highlight_data['data']:
                    reels_media = highlight_data['data']['reels_media']
                    if reels_media and len(reels_media) > 0 and 'items' in reels_media[0]:
                        media_items = reels_media[0]['items']
                        self.update_result_text_widget(self.highlights_result_text, f"✅ Highlight medya içeriği bulundu: {len(media_items)} öğe\n")
                
                # Alternatif path: data.reels.{highlight_id}.items
                if not media_items and 'data' in highlight_data and 'reels' in highlight_data['data']:
                    reels = highlight_data['data']['reels']
                    if highlight_id in reels and 'items' in reels[highlight_id]:
                        media_items = reels[highlight_id]['items']
                        self.update_result_text_widget(self.highlights_result_text, f"✅ Medya içeriği alternatif yoldan bulundu: {len(media_items)} öğe\n")
                
                # Medya bulunamadıysa JSON yapısını incele ve manuel giriş iste
                if not media_items:
                    self.update_result_text_widget(self.highlights_result_text, f"❌ Medya içeriği bulunamadı. API yanıt yapısı inceleniyor...\n")
                    debug_str = f"API yanıt verileri (ilk 500 karakter):\n{json.dumps(highlight_data)[:500]}...\n"
                    self.update_result_text_widget(self.highlights_result_text, debug_str)
                    
                    # Kullanıcıdan manuel JSON yolu al
                    manual_path = simpledialog.askstring("Medya İçeriğini Manuel Bul", 
                                                       f"'{title}' öne çıkan hikayesinin medya içeriği otomatik bulunamadı.\n\n"
                                                       "API yanıt çıktısında medya öğelerinin listesini içeren JSON yolunu\n"
                                                       "nokta ile ayırarak girin (örn: 'data.reels_media.0.items'):")
                    
                    if not manual_path:
                        self.update_result_text_widget(self.highlights_result_text, "❌ İşlem iptal edildi.\n")
                        return False
                    
                    try:
                        # Nokta notasyonu ile verilen yolu takip et
                        parts = manual_path.split('.')
                        current = highlight_data
                        
                        for part in parts:
                            if part.isdigit():
                                current = current[int(part)]
                            else:
                                current = current.get(part, {})
                        
                        if isinstance(current, list):
                            media_items = current
                            self.update_result_text_widget(self.highlights_result_text, f"✅ Medya içeriği manuel yoldan bulundu: {len(media_items)} öğe\n")
                        else:
                            self.update_result_text_widget(self.highlights_result_text, "❌ Belirtilen yolda liste tipi medya verisi bulunamadı.\n")
                            return False
                    except KeyError as e:
                        self.update_result_text_widget(self.highlights_result_text, f"❌ Belirtilen anahtar bulunamadı: {str(e)}\n")
                        return False
                    except IndexError as e:
                        self.update_result_text_widget(self.highlights_result_text, f"❌ Belirtilen indeks bulunamadı: {str(e)}\n")
                        return False
                    except Exception as e:
                        self.update_result_text_widget(self.highlights_result_text, f"❌ Manuel yol işlenirken hata: {str(e)}\n")
                        return False
                
                if not media_items:
                    self.update_result_text_widget(self.highlights_result_text, f"❌ '{title}' için indirilebilir medya bulunamadı.\n")
                    return False
                
                # Highlight medyalarını indir
                downloaded_count = 0
                
                for i, item in enumerate(media_items):
                    # Medya ID'si ve zaman damgası
                    media_id = item.get('id', f"unknown_{i}")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Video mu resim mi?
                    is_video = item.get('is_video', False)
                    
                    if is_video:
                        # Video URL'sini bul
                        video_url = None
                        
                        # Ana video URL'si
                        if 'video_versions' in item and len(item['video_versions']) > 0:
                            video_url = item['video_versions'][0].get('url')
                        # Alternatif video yapısı
                        elif 'video_resources' in item and len(item['video_resources']) > 0:
                            video_url = item['video_resources'][0].get('src')
                        
                        if not video_url:
                            self.update_result_text_widget(self.highlights_result_text, f"⚠️ Video URL'si bulunamadı: {media_id}\n")
                            continue
                        
                        # Dosya adı ve yolu
                        video_filename = f"{username}_highlight_{title}_{media_id}_{timestamp}.mp4"
                        video_path = highlight_dir / video_filename
                        
                        # Video indir
                        self.update_result_text_widget(self.highlights_result_text, f"⏳ Video indiriliyor [{i+1}/{len(media_items)}]: {media_id}\n")
                        try:
                            # Timeout ekle
                            video_response = requests.get(video_url, stream=True, timeout=(30, 120))
                            with open(video_path, 'wb') as f:
                                for chunk in video_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            downloaded_count += 1
                            self.update_result_text_widget(self.highlights_result_text, f"✅ Video indirildi: {video_filename}\n")
                        except requests.exceptions.Timeout:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Video indirirken zaman aşımı: {media_id}\n")
                        except requests.exceptions.ConnectionError:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Video indirirken bağlantı hatası: {media_id}\n")
                        except IOError as e:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Video dosyasına yazma hatası: {str(e)}\n")
                        except Exception as e:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Video indirme hatası: {str(e)}\n")
                    else:
                        # Resim URL'sini bul
                        image_url = None
                        
                        # Ana resim URL'si
                        if 'image_versions2' in item and 'candidates' in item['image_versions2']:
                            candidates = item['image_versions2']['candidates']
                            if candidates and len(candidates) > 0:
                                image_url = candidates[0].get('url')
                        # Alternatif resim yapısı
                        elif 'display_resources' in item and len(item['display_resources']) > 0:
                            # En yüksek çözünürlüklü resmi al
                            sorted_resources = sorted(item['display_resources'], 
                                                    key=lambda x: x.get('config_width', 0), 
                                                    reverse=True)
                            image_url = sorted_resources[0].get('src')
                        
                        if not image_url:
                            self.update_result_text_widget(self.highlights_result_text, f"⚠️ Resim URL'si bulunamadı: {media_id}\n")
                            continue
                        
                        # Dosya adı ve yolu
                        image_filename = f"{username}_highlight_{title}_{media_id}_{timestamp}.jpg"
                        image_path = highlight_dir / image_filename
                        
                        # Resim indir
                        self.update_result_text_widget(self.highlights_result_text, f"⏳ Resim indiriliyor [{i+1}/{len(media_items)}]: {media_id}\n")
                        try:
                            # Timeout ekle
                            image_response = requests.get(image_url, timeout=(30, 60))
                            with open(image_path, 'wb') as f:
                                f.write(image_response.content)
                            downloaded_count += 1
                            self.update_result_text_widget(self.highlights_result_text, f"✅ Resim indirildi: {image_filename}\n")
                        except requests.exceptions.Timeout:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Resim indirirken zaman aşımı: {media_id}\n")
                        except requests.exceptions.ConnectionError:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Resim indirirken bağlantı hatası: {media_id}\n")
                        except IOError as e:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Resim dosyasına yazma hatası: {str(e)}\n")
                        except Exception as e:
                            self.update_result_text_widget(self.highlights_result_text, f"❌ Resim indirme hatası: {str(e)}\n")
                
                if downloaded_count > 0:
                    self.update_result_text_widget(self.highlights_result_text, f"\n✅ '{title}' öne çıkan hikayesi başarıyla indirildi ({downloaded_count}/{len(media_items)} medya)\n")
                    self.update_result_text_widget(self.highlights_result_text, f"📂 İndirilen medyalar: {highlight_dir}\n")
                    self.update_status(f"'{title}' öne çıkan hikayesi başarıyla indirildi")
                    return True
                else:
                    self.update_result_text_widget(self.highlights_result_text, f"❌ '{title}' öne çıkan hikayesinden hiç bir medya indirilemedi.\n")
                    self.update_status(f"'{title}' öne çıkan hikayesi indirilirken bir hata oluştu")
                    return False
                    
            except json.JSONDecodeError as e:
                self.update_result_text_widget(self.highlights_result_text, f"❌ API yanıtı JSON formatında değil: {str(e)}\n")
                self.update_status(f"'{title}' öne çıkan hikayesi indirilirken bir hata oluştu")
                return False
            except Exception as e:
                self.update_result_text_widget(self.highlights_result_text, f"❌ Highlight verisi ayrıştırılırken hata: {str(e)}\n")
                self.update_status(f"'{title}' öne çıkan hikayesi indirilirken bir hata oluştu")
                return False
                
        except Exception as e:
            self.update_result_text_widget(self.highlights_result_text, f"❌ Hata: {str(e)}\n")
            messagebox.showerror("Hata", f"Öne çıkan hikaye indirilirken bir hata oluştu: {str(e)}")
            return False
    
    def _download_all_highlights_thread(self, username, highlights):
        """Arka planda tüm öne çıkan hikayeleri indir."""
        try:
            self.update_status(f"{username} kullanıcısının tüm öne çıkan hikayeleri indiriliyor...")
            self.update_result_text_widget(self.highlights_result_text, f"\n⏳ {len(highlights)} adet öne çıkan hikaye indiriliyor...\n")
            
            base_dir = self.stalker.content_types["stories"] / username / "highlights"
            base_dir.mkdir(exist_ok=True, parents=True)
            
            success_count = 0
            fail_count = 0
            
            for i, highlight in enumerate(highlights, 1):
                title = highlight['title']
                self.update_result_text_widget(self.highlights_result_text, f"⏳ [{i}/{len(highlights)}] '{title}' öne çıkan hikayesi indiriliyor...\n")
                
                try:
                    success = self._download_highlight_thread(username, highlight)
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                        self.update_result_text_widget(self.highlights_result_text, f"❌ '{title}' öne çıkan hikayesi indirilemedi\n")
                except Exception as e:
                    fail_count += 1
                    self.update_result_text_widget(self.highlights_result_text, f"❌ '{title}' indirilirken hata: {str(e)}\n")
            
            summary = f"\n✅ Toplam {len(highlights)} öne çıkan hikayeden {success_count} tanesi başarıyla indirildi"
            if fail_count > 0:
                summary += f", {fail_count} tanesi başarısız oldu"
                
            self.update_result_text_widget(self.highlights_result_text, summary + "\n")
            self.update_status(f"{username} kullanıcısının öne çıkan hikayeleri indirildi ({success_count}/{len(highlights)})")
            
        except Exception as e:
            self.update_result_text_widget(self.highlights_result_text, f"❌ Hata: {str(e)}\n")
            messagebox.showerror("Hata", f"Öne çıkan hikayeler indirilirken bir hata oluştu: {str(e)}")

    def _get_user_id_from_profile(self, username):
        """
        Get user ID from Instagram profile page
        """
        self.update_status(f"{self._('reading_profile')} {username}...")
        
        cookies = self.stalker.get_cookies_dict()
        if not cookies:
            return None
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Accept-Language": "tr-TR, en-US",
        }
        
        try:
            # Make request to get the profile page
            url = f"https://www.instagram.com/{username}/"
            response = requests.get(
                url, 
                headers=headers, 
                cookies=cookies,
                timeout=(10, 30)  # 10 sec connection, 30 sec read timeout
            )
            response.raise_for_status()
            
            # Method 1: Search for user ID in script tag
            import re
            user_id_match = re.search(r'"user_id":"(\d+)"', response.text)
            if user_id_match:
                return user_id_match.group(1)
            
            # Method 2: Extract from profile picture URL
            profile_pic_match = re.search(r'profile_pic_url_hd":"[^"]+/(\d+)/', response.text)
            if profile_pic_match:
                return profile_pic_match.group(1)
            
            # Method 3: Find the most common numeric ID in the content
            # This is a fallback method
            self.update_status(f"{self._('extracting_user_id')} {username}...")
            
            all_ids = re.findall(r'"id":"(\d+)"', response.text)
            if not all_ids:
                all_ids = re.findall(r'"id":(\d+)', response.text)
                
            if all_ids:
                from collections import Counter
                id_counts = Counter(all_ids)
                common_ids = id_counts.most_common()
                
                if common_ids and len(common_ids) > 0:
                    return common_ids[0][0]  # Return the most common ID
            
            # If we reach here, we couldn't find the ID automatically
            self.update_status(f"{self._('user_id_not_found')}")
            
            # Ask user to input ID manually through dialog
            if is_main_thread():
                user_id = self._ask_for_user_id(username)
                return user_id
            else:
                # We're in a background thread, we need to schedule the dialog on the main thread
                result = []
                
                def ask_in_main():
                    user_id = self._ask_for_user_id(username)
                    result.append(user_id)
                
                self.after(0, ask_in_main)
                
                # Wait for the result (this is not ideal, but necessary for threading)
                timeout = 60  # Wait up to 60 seconds for user input
                start_time = time.time()
                while not result and time.time() - start_time < timeout:
                    time.sleep(0.1)
                
                return result[0] if result else None
                
        except Exception as e:
            self.update_status(f"{self._('error_getting_user_id')}: {e}")
            return None
            
    def _ask_for_user_id(self, username):
        """Show dialog asking user to input Instagram user ID manually"""
        instructions = self._("user_id_instructions").format(username=username)
        user_id = simpledialog.askstring(
            self._("user_id_required"),
            instructions
        )
        return user_id

    def update_log(self, text):
        """Log sekmesine yeni satır ekle"""
        def _update():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{text}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        if is_main_thread():
            _update()
        else:
            self.after(0, _update)
    
    def clear_log(self):
        """Log sekmesinin içeriğini temizle"""
        def _update():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        if is_main_thread():
            _update()
        else:
            self.after(0, _update)
    
    def capture_output(self, func):
        """Capture output of a function and return it as a string"""
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            result = func()
            output = sys.stdout.getvalue()
            return result, output
        finally:
            sys.stdout = old_stdout

    def download_reels(self):
        """Download reels of given username"""
        username = self.username_entry3.get().strip()
        if not username:
            messagebox.showerror(self._("error"), self._("enter_username"))
            return
        
        limit = simpledialog.askinteger(
            self._("reel_limit"), 
            self._("reel_limit_prompt"),
            initialvalue=5,
            minvalue=1,
            maxvalue=50
        )
        
        if limit is None:
            return  # User cancelled the dialog
        
        # Set current text widget
        self.current_text_widget = self.reel_result_text
        
        # Clear previous results and update status
        self.update_result_text("", append=False)
        self.update_status(f"{self._('downloading_reels')} {username} ({limit} reels)...")

    def get_cookies_dict(self):
        """Get cookies as dictionary for API requests.
        This is a helper method needed in the GUI to check if cookies are set.
        """
        if hasattr(self, 'cookies_dict') and self.cookies_dict:
            return self.cookies_dict
        return None


def main():
    """Ana fonksiyon - GUI uygulamasını başlat."""
    app = InstaStalkGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
    