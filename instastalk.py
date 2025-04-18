#!/usr/bin/env python3
import os
import json
import argparse
import getpass
import time
import re
import requests
import shutil
from datetime import datetime
from pathlib import Path
import sys
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import uuid
import tempfile
import traceback
import gzip
try:
    import brotli
except ImportError:
    print("Installing brotli library...")
    import subprocess
    subprocess.check_call(["pip", "install", "brotli"])
    import brotli

try:
    from instacapture import InstaStory, InstaPost
except ImportError:
    print("InstaCapture kütüphanesi bulunamadı. Yükleniyor...")
    import subprocess
    subprocess.check_call(["pip", "install", "instacapture"])
    from instacapture import InstaStory, InstaPost


# Dil çevirileri
TRANSLATIONS = {
    "tr": {
        "app_title": "📲 InstaStalker - Instagram İçerik İndirme Aracı",
        "lib_missing": "InstaCapture kütüphanesi bulunamadı. Yükleniyor...",
        "cookies_loaded": "✅ Kaydedilmiş çerezler yüklendi: {0}",
        "cookies_not_loaded": "❌ Çerezler yüklenemedi: {0}",
        "cookies_saved": "✅ Çerezler kaydedildi: {0}",
        "cookies_not_saved": "❌ Çerezler kaydedilemedi: {0}",
        "sessionid_warning": "⚠️ Uyarı: Cookie içinde 'sessionid' bulunamadı! Bu olmadan hikayeler görüntülenemez.",
        "cookies_needed": "\n📋 Instagram hikayelerini indirmek için çerezlere ihtiyacımız var",
        "cookie_steps": [
            "Aşağıdaki adımları takip edin:",
            "1. Chrome/Safari'de Instagram.com adresine gidin ve giriş yapın",
            "2. Tarayıcıda herhangi bir yere sağ tıklayın ve 'İncele' seçeneğini seçin",
            "3. Açılan geliştirici araçlarında 'Ağ' sekmesine tıklayın",
            "4. Sayfayı yenileyin (F5)",
            "5. 'instagram.com' ile başlayan bir isteği seçin",
            "6. 'Başlıklar' sekmesinde 'Request Headers' kısmında 'Cookie:' satırını bulun",
            "7. Cookie satırını tam olarak kopyalayın"
        ],
        "cookie_paste": "\n🍪 Cookie değerini yapıştırın: ",
        "no_cookies": "❌ Hikaye indirmek için çerezler gereklidir.",
        "downloading_stories": "\n⏳ {0} kullanıcısının hikayeleri indiriliyor...",
        "stories_success": "✅ {0} için {1} hikaye indirildi ({2:.1f} saniye)",
        "story_item": "  {0}. {1} - {2}",
        "media_video": "🎥 Video",
        "media_image": "🖼️ Resim",
        "unknown_time": "Bilinmeyor",
        "stories_saved": "\nHikayeler '{0}' klasörüne kaydedildi",
        "stories_not_found": "❌ {0} kullanıcısının hikayeleri bulunamadı veya özel hesap olabilir",
        "story_error": "❌ Hikayeler indirilirken bir hata oluştu: {0}",
        "downloading_post": "\n⏳ Gönderi indiriliyor: {0}",
        "downloading_posts": "\n⏳ {0} kullanıcısının son {1} gönderisi indiriliyor...",
        "post_success": "✅ '{0}' kullanıcısının gönderisi indirildi ({1:.1f} saniye)",
        "posts_success": "✅ {0} kullanıcısının {1}/{2} gönderisi indirildi ({3:.1f} saniye)",
        "post_saved": "\nMedya '{0}' klasörüne kaydedildi",
        "post_media_not_found": "❌ Gönderi medyası bulunamadı",
        "post_not_found": "❌ Gönderi bulunamadı veya gizli olabilir",
        "post_error": "❌ Gönderi indirilirken bir hata oluştu: {0}",
        "posts_not_found": "❌ {0} kullanıcısının gönderileri bulunamadı veya özel hesap olabilir",
        "no_posts_found": "❌ {0} kullanıcısının hiç gönderisi bulunamadı",
        "downloading_profile": "\n⏳ {0} kullanıcısının profil resmi indiriliyor...",
        "profile_success": "✅ {0} kullanıcısının profil resmi indirildi",
        "profile_saved": "\nProfil resmi '{0}' dosyasına kaydedildi",
        "profile_not_found": "❌ {0} kullanıcısının profil resmi bulunamadı",
        "profile_download_error": "❌ Profil resmi indirilemedi. HTTP Hata: {0}",
        "user_not_found": "❌ {0} kullanıcısı bulunamadı. HTTP Hata: {1}",
        "profile_error": "❌ Profil resmi indirilirken bir hata oluştu: {0}",
        "downloads_title": "\n📂 İndirilen Dosyalar:",
        "downloads_stories": "  📱 Hikayeler:",
        "downloads_posts": "  🖼️ Gönderiler:",
        "downloads_profiles": "  👤 Profil Resimleri:",
        "downloads_item": "    - {0} ({1} {2})",
        "downloads_media": "medya",
        "downloads_post": "gönderi",
        "downloads_image": "resim",
        "downloads_empty": "  Henüz indirilmiş dosya bulunmuyor.",
        "clean_confirm": "⚠️ Tüm indirilen dosyalar silinecek. Emin misiniz? (e/H): ",
        "clean_success": "✅ Tüm indirilen dosyalar temizlendi.",
        "clean_cancel": "İşlem iptal edildi.",
        "app_name": "\n🔍 Instagram Stalker Tool 🔍",
        "menu_download_story": "1. Hikaye İndir",
        "menu_download_post": "2. Gönderi/Reel İndir",
        "menu_download_profile": "3. Profil Resmi İndir",
        "menu_batch_download": "4. Toplu İndirme",
        "menu_set_cookies": "5. Çerezleri Ayarla",
        "menu_list_downloads": "6. İndirilen Dosyaları Listele",
        "menu_clean": "7. Tüm İndirilen Dosyaları Temizle",
        "menu_lang": "8. Dil Değiştir (Change Language)",
        "menu_exit": "9. Çıkış",
        "menu_choice": "\nSeçiminiz (1-9): ",
        "username_prompt": "Hikayeleri indirilecek kullanıcı adı: ",
        "post_url_prompt": "Gönderi veya reel URL'si: ",
        "username_prompt": "Profil resmi indirilecek kullanıcı adı: ",
        "invalid_choice": "Geçersiz seçim!",
        "exit_message": "Çıkılıyor...",
        "interrupt_message": "\n\nİşlem kullanıcı tarafından durduruldu. Çıkılıyor...",
        "unexpected_error": "\n❌ Beklenmeyen bir hata oluştu: {0}",
        "lang_selection": "\nDil seçin / Select language:",
        "lang_tr": "1. Türkçe",
        "lang_en": "2. English",
        "lang_choice": "Seçiminiz / Your choice (1-2): ",
        "lang_changed": "✅ Dil değiştirildi: {0}",
        "yes_short": "e",
        "batch_username_prompt": "Toplu indirme yapılacak kullanıcı adı: ",
        "batch_options": "\nNeyi indirmek istiyorsunuz?",
        "batch_option_stories": "1. Hikayeler",
        "batch_option_posts": "2. Son Gönderiler (en son 12)",
        "batch_option_both": "3. Her İkisi de",
        "batch_option_choice": "Seçiminiz (1-3): ",
        "batch_download_start": "\n⏳ {0} kullanıcısı için toplu indirme başlatılıyor...",
        "batch_download_complete": "✅ Toplu indirme tamamlandı!",
        "batch_download_error": "❌ Toplu indirme sırasında bir hata oluştu: {0}",
        "menu_9": "9. Çerez Şifrelemeyi Aç/Kapat",
        "encryption_enabled": "✅ Çerez şifreleme aktif edildi. Çerezleriniz artık şifreli olarak saklanacak.",
        "encryption_disabled": "❌ Çerez şifreleme devre dışı bırakıldı. Çerezleriniz şifrelenmeden saklanacak.",
        "enabling_encryption": "⏳ Çerez şifreleme etkinleştiriliyor...",
        "disabling_encryption": "⏳ Çerez şifreleme devre dışı bırakılıyor...",
        "encryption_error": "🔒 Şifreleme hatası: {0}",
        "encryption_info": "🔒 Çerez şifreleme durumu: {0}",
        "menu_10": "10. Öne Çıkan Hikayeleri İndir",
        "highlight_username_prompt": "Öne çıkan hikayeleri indirilecek kullanıcı adı: ",
        "downloading_highlights": "\n⏳ {0} kullanıcısının öne çıkan hikayeleri alınıyor...",
        "no_highlights_found": "❌ {0} kullanıcısının öne çıkan hikayeleri bulunamadı veya özel hesap olabilir",
        "highlight_selection": "\n📌 Öne çıkan hikayeler:",
        "highlight_item": "  {0}. {1} ({2} hikaye)",
        "highlight_choice": "\nİndirmek istediğiniz öne çıkan hikayeyi seçin (0: İptal): ",
        "highlight_all": "  A. Tüm öne çıkan hikayeleri indir",
        "downloading_highlight": "\n⏳ Downloading highlight '{0}'...",
        "highlight_success": "✅ Downloaded highlight '{0}' ({1} stories)",
        "highlight_saved": "\nHighlight stories saved to '{0}' folder",
        "highlight_error": "❌ Error downloading highlight stories: {0}",
        "highlight_cancel": "ℹ️ Operation canceled.",
    },
    "en": {
        "app_title": "📲 InstaStalker - Instagram Content Downloader Tool",
        "lib_missing": "InstaCapture library not found. Installing...",
        "cookies_loaded": "✅ Saved cookies loaded: {0}",
        "cookies_not_loaded": "❌ Cookies could not be loaded: {0}",
        "cookies_saved": "✅ Cookies saved: {0}",
        "cookies_not_saved": "❌ Cookies could not be saved: {0}",
        "sessionid_warning": "⚠️ Warning: 'sessionid' not found in cookies! Stories cannot be viewed without it.",
        "cookies_needed": "\n📋 We need cookies to download Instagram stories",
        "cookie_steps": [
            "Follow these steps:",
            "1. Go to Instagram.com in Chrome/Safari and log in",
            "2. Right-click anywhere and select 'Inspect'",
            "3. Go to the 'Network' tab in the developer tools",
            "4. Refresh the page (F5)",
            "5. Select a request starting with 'instagram.com'",
            "6. In the 'Headers' tab, find 'Cookie:' in the 'Request Headers' section",
            "7. Copy the entire cookie line"
        ],
        "cookie_paste": "\n🍪 Paste the cookie value: ",
        "no_cookies": "❌ Cookies are required to download stories.",
        "downloading_stories": "\n⏳ Downloading stories for user {0}...",
        "stories_success": "✅ Downloaded {1} stories for {0} ({2:.1f} seconds)",
        "story_item": "  {0}. {1} - {2}",
        "media_video": "🎥 Video",
        "media_image": "🖼️ Image",
        "unknown_time": "Unknown",
        "stories_saved": "\nStories saved to '{0}' folder",
        "stories_not_found": "❌ Stories for user {0} not found or account is private",
        "story_error": "❌ Error downloading stories: {0}",
        "downloading_post": "\n⏳ Downloading post: {0}",
        "downloading_posts": "\n⏳ Downloading last {1} posts for user {0}...",
        "post_success": "✅ Downloaded post from '{0}' ({1:.1f} seconds)",
        "posts_success": "✅ Downloaded {1}/{2} posts from {0} ({3:.1f} seconds)",
        "post_saved": "\nMedia saved to '{0}' folder",
        "post_media_not_found": "❌ Post media not found",
        "post_not_found": "❌ Post not found or is private",
        "post_error": "❌ Error downloading post: {0}",
        "posts_not_found": "❌ Posts for user {0} not found or account is private",
        "no_posts_found": "❌ No posts found for user {0}",
        "downloading_profile": "\n⏳ Downloading profile picture for {0}...",
        "profile_success": "✅ Downloaded profile picture for {0}",
        "profile_saved": "\nProfile picture saved to '{0}'",
        "profile_not_found": "❌ Profile picture for {0} not found",
        "profile_download_error": "❌ Could not download profile picture. HTTP Error: {0}",
        "user_not_found": "❌ User {0} not found. HTTP Error: {1}",
        "profile_error": "❌ Error downloading profile picture: {0}",
        "downloads_title": "\n📂 Downloaded Files:",
        "downloads_stories": "  📱 Stories:",
        "downloads_posts": "  🖼️ Posts:",
        "downloads_profiles": "  👤 Profile Pictures:",
        "downloads_item": "    - {0} ({1} {2})",
        "downloads_media": "media",
        "downloads_post": "post",
        "downloads_image": "image",
        "downloads_empty": "  No downloaded files yet.",
        "clean_confirm": "⚠️ All downloaded files will be deleted. Are you sure? (y/N): ",
        "clean_success": "✅ All downloaded files have been cleaned.",
        "clean_cancel": "Operation canceled.",
        "app_name": "\n🔍 Instagram Stalker Tool 🔍",
        "menu_download_story": "1. Download Story",
        "menu_download_post": "2. Download Post/Reel",
        "menu_download_profile": "3. Download Profile Picture",
        "menu_batch_download": "4. Batch Download",
        "menu_set_cookies": "5. Set Cookies",
        "menu_list_downloads": "6. List Downloaded Files",
        "menu_clean": "7. Clean All Downloaded Files",
        "menu_lang": "8. Change Language (Dil Değiştir)",
        "menu_exit": "9. Exit",
        "menu_choice": "\nYour choice (1-9): ",
        "username_prompt": "Username for stories to download: ",
        "post_url_prompt": "Post or reel URL: ",
        "username_prompt": "Username for profile picture to download: ",
        "invalid_choice": "Invalid choice!",
        "exit_message": "Exiting...",
        "interrupt_message": "\n\nOperation interrupted by user. Exiting...",
        "unexpected_error": "\n❌ An unexpected error occurred: {0}",
        "lang_selection": "\nSelect language / Dil seçin:",
        "lang_tr": "1. Türkçe",
        "lang_en": "2. English",
        "lang_choice": "Your choice / Seçiminiz (1-2): ",
        "lang_changed": "✅ Language changed to: {0}",
        "yes_short": "y",
        "batch_username_prompt": "Username for batch download: ",
        "batch_options": "\nWhat would you like to download?",
        "batch_option_stories": "1. Stories",
        "batch_option_posts": "2. Recent Posts (latest 12)",
        "batch_option_both": "3. Both",
        "batch_option_choice": "Your choice (1-3): ",
        "batch_download_start": "\n⏳ Starting batch download for user {0}...",
        "batch_download_complete": "✅ Batch download completed!",
        "batch_download_error": "❌ Error during batch download: {0}",
        "menu_9": "9. Toggle Cookie Encryption",
        "encryption_enabled": "✅ Cookie encryption enabled. Your cookies will now be stored encrypted.",
        "encryption_disabled": "❌ Cookie encryption disabled. Your cookies will be stored unencrypted.",
        "enabling_encryption": "⏳ Enabling cookie encryption...",
        "disabling_encryption": "⏳ Disabling cookie encryption...",
        "encryption_error": "🔒 Encryption error: {0}",
        "encryption_info": "🔒 Cookie encryption status: {0}",
        "menu_10": "10. Download Highlight Stories",
        "highlight_username_prompt": "Username for highlights to download: ",
        "downloading_highlights": "\n⏳ Fetching highlight stories for user {0}...",
        "no_highlights_found": "❌ Highlight stories for user {0} not found or account is private",
        "highlight_selection": "\n📌 Highlight stories:",
        "highlight_item": "  {0}. {1} ({2} stories)",
        "highlight_choice": "\nSelect highlight to download (0: Cancel): ",
        "highlight_all": "  A. Download all highlights",
        "downloading_highlight": "\n⏳ Downloading highlight '{0}'...",
        "highlight_success": "✅ Downloaded highlight '{0}' ({1} stories)",
        "highlight_saved": "\nHighlight stories saved to '{0}' folder",
        "highlight_error": "❌ Error downloading highlight stories: {0}",
        "highlight_cancel": "ℹ️ Operation canceled.",
    }
}


class InstaStalker:
    """Instagram hikayelerini ve gönderilerini indirmek için kullanıcı dostu bir araç."""
    
    def __init__(self):
        self.cookies = {}
        self.config_dir = Path.home() / ".instastalk"
        self.config_dir.mkdir(exist_ok=True)
        self.cookies_file = self.config_dir / "cookies.json"
        self.settings_file = self.config_dir / "settings.json"
        self.salt_file = self.config_dir / ".salt"
        
        # Varsayılan ayarlar
        self.settings = {
            "language": "tr",
            "encryption_enabled": False
        }
        
        # Ayarları yükle
        self.load_settings()
        
        # Ana dizin yapısı
        self.base_dir = Path("./instagram_content")
        self.base_dir.mkdir(exist_ok=True)
        
        # İçerik tipine göre alt dizinler
        self.content_types = {
            "stories": self.base_dir / "stories",
            "posts": self.base_dir / "posts",
            "profiles": self.base_dir / "profiles"
        }
        
        # Alt dizinleri oluştur
        for dir_path in self.content_types.values():
            dir_path.mkdir(exist_ok=True)
        
        # Çerezleri yükle (eğer varsa)
        self.load_cookies()
    
    def _(self, key, *args):
        """Metni çeviri sözlüğünden alır ve biçimlendirir."""
        lang = self.settings["language"]
        if lang not in TRANSLATIONS:
            lang = "tr"  # Varsayılan dil
        
        text = TRANSLATIONS[lang].get(key, key)
        if args:
            return text.format(*args)
        return text
    
    def load_settings(self):
        """Kullanıcı ayarlarını yükle."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except Exception:
                # Ayarlar yüklenemezse varsayılan ayarları kullan
                pass
    
    def save_settings(self):
        """Kullanıcı ayarlarını kaydet."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f)
            return True
        except Exception:
            return False
    
    def change_language(self):
        """Dil değiştirme menüsünü göster ve dil değiştir."""
        print(self._("lang_selection"))
        print(self._("lang_tr"))
        print(self._("lang_en"))
        
        choice = input(self._("lang_choice"))
        
        if choice == "1":
            self.settings["language"] = "tr"
            self.save_settings()
            print(self._("lang_changed", "Türkçe"))
        elif choice == "2":
            self.settings["language"] = "en"
            self.save_settings()
            print(self._("lang_changed", "English"))
    
    def generate_salt(self):
        """Şifreleme için tuz değeri oluşturur veya var olanı yükler."""
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            # Yeni tuz oluştur
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            os.chmod(self.salt_file, 0o600)  # Sadece kullanıcı erişebilsin
            return salt
    
    def get_encryption_key(self, password=None):
        """Şifreleme anahtarı oluşturur."""
        if password is None:
            # Kullanıcı adını ve makine adını kullanarak bir şifre oluştur
            # Bu sadece hafif bir güvenlik sağlar, şifreyi gizlemek için değil
            user = getpass.getuser()
            hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            password = f"{user}@{hostname}"
        
        salt = self.generate_salt()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_data(self, data, password=None):
        """JSON veriyi şifreler ve şifrelenmiş metin döndürür."""
        if not data:
            return None
            
        key = self.get_encryption_key(password)
        fernet = Fernet(key)
        
        # JSON verisini metin haline getir
        json_text = json.dumps(data).encode('utf-8')
        
        # Şifrele
        encrypted_data = fernet.encrypt(json_text)
        
        return encrypted_data
    
    def decrypt_data(self, encrypted_data, password=None):
        """Şifrelenmiş metni çözer ve JSON olarak döndürür."""
        if not encrypted_data:
            return {}
            
        try:
            key = self.get_encryption_key(password)
            fernet = Fernet(key)
            
            # Şifreyi çöz
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # JSON'a dönüştür
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            print(self._("encryption_error", str(e)))
            return {}
    
    def load_cookies(self):
        """Kaydedilmiş çerezleri yükle."""
        if self.cookies_file.exists():
            try:
                if self.settings.get("encryption_enabled", False):
                    # Şifrelenmiş çerezleri yükle
                    with open(self.cookies_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    self.cookies = self.decrypt_data(encrypted_data)
                else:
                    # Normal JSON formatında yükle
                    with open(self.cookies_file, 'r') as f:
                        self.cookies = json.load(f)
                
                if self.cookies:
                    cookie_keys = ', '.join(self.cookies.keys())
                    print(self._("cookies_loaded", cookie_keys))
                    return True
                
            except Exception as e:
                print(self._("cookies_not_loaded", str(e)))
        return False
    
    def save_cookies(self):
        """Çerezleri kaydet."""
        try:
            if self.settings.get("encryption_enabled", False):
                # Çerezleri şifrele ve kaydet
                encrypted_data = self.encrypt_data(self.cookies)
                with open(self.cookies_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # Normal JSON formatında kaydet
                with open(self.cookies_file, 'w') as f:
                    json.dump(self.cookies, f)
            
            # Dosya izinlerini ayarla
            os.chmod(self.cookies_file, 0o600)  # Sadece kullanıcı okuyabilir/yazabilir
            
            cookie_keys = ', '.join(self.cookies.keys())
            print(self._("cookies_saved", cookie_keys))
            return True
        except Exception as e:
            print(self._("cookies_not_saved", str(e)))
            return False
    
    
    def toggle_encryption(self):
        """Çerez şifrelemeyi aç/kapat."""
        current_status = self.settings.get("encryption_enabled", False)
        new_status = not current_status
        
        # Şifrelemeyi etkinleştiriyorsak ve çerezler varsa, çerezleri yükle, şifrele ve kaydet
        if new_status and self.cookies:
            print(self._("enabling_encryption"))
            self.settings["encryption_enabled"] = new_status
            self.save_settings()  # Önce yeni durumu kaydet
            self.save_cookies()   # Çerezleri şifreli olarak kaydet
            print(self._("encryption_enabled"))
        
        # Şifrelemeyi devre dışı bırakıyorsak ve çerezler varsa, çerezleri yükle ve şifresiz kaydet
        elif not new_status and self.cookies_file.exists():
            print(self._("disabling_encryption"))
            # Şifrelenmiş çerezleri yükle (şu anda şifreli olmalı)
            old_encryption_status = self.settings.get("encryption_enabled", False)
            
            # Eğer şifreleme açıksa, çerezleri yüklemeden önce şifreleme ayarını değiştirme
            if old_encryption_status:
                loaded_cookies = {}
                try:
                    with open(self.cookies_file, 'rb') as f:
                        encrypted_data = f.read()
                    loaded_cookies = self.decrypt_data(encrypted_data)
                except Exception as e:
                    print(self._("cookies_not_loaded", str(e)))
                
                # Şifrelemeyi kapat ve çerezleri güncelle
                self.settings["encryption_enabled"] = new_status
                self.save_settings()
                
                # Çerezleri tekrar ayarla ve şifresiz kaydet
                self.cookies = loaded_cookies
                self.save_cookies()
            else:
                # Zaten şifreleme kapalıysa, sadece ayarı güncelle
                self.settings["encryption_enabled"] = new_status
                self.save_settings()
            
            print(self._("encryption_disabled"))
        
        # Çerez yoksa, sadece ayarı değiştir
        else:
            self.settings["encryption_enabled"] = new_status
            self.save_settings()
            
            if new_status:
                print(self._("encryption_enabled"))
            else:
                print(self._("encryption_disabled"))
                
    def set_cookies_from_string(self, cookie_str):
        """Cookie string'inden çerezleri ayarla."""
        # Cookie: header formatından temizle
        if cookie_str.strip().startswith("Cookie:"):
            cookie_str = cookie_str.replace("Cookie:", "").strip()
        
        # Çerezleri işle
        cookie_pairs = cookie_str.split(";")
        for pair in cookie_pairs:
            if "=" in pair:
                key, value = pair.strip().split("=", 1)
                self.cookies[key] = value
        
        # sessionid kontrolü
        if "sessionid" not in self.cookies:
            print(self._("sessionid_warning"))
            return False
        
        self.save_cookies()
        return True

    def get_interactive_cookies(self):
        """Kullanıcıdan etkileşimli olarak çerezleri al."""
        print(self._("cookies_needed"))
        for step in self._("cookie_steps"):
            print(step)
        
        cookie_str = input(self._("cookie_paste"))
        return self.set_cookies_from_string(cookie_str)
    
    def download_story(self, username):
        """Belirtilen kullanıcının hikayelerini indir."""
        if not self.cookies:
            print(self._("no_cookies"))
            if not self.get_interactive_cookies():
                return False
        
        try:
            # Kullanıcı klasörünü oluştur
            user_dir = self.content_types["stories"] / username
            user_dir.mkdir(exist_ok=True)
            
            # Geçici bir klasör oluştur
            temp_dir = Path("./temp_story")
            temp_dir.mkdir(exist_ok=True)
            
            # InstaStory nesnesini oluştur
            story_obj = InstaStory()
            story_obj.cookies = self.cookies
            
            # InstaCapture kütüphanesi için ilgili diğer attributes
            # cookies'i farklı bir formatta (dict olarak) bekliyorsa bunu da sağlayalım
            if hasattr(story_obj, 'cookies_dict'):
                story_obj.cookies_dict = self.cookies
            
            story_obj.username = username
            story_obj.folder_path = str(temp_dir)
            
            # İndirme başlangıcını göster
            print(self._("downloading_stories", username))
            start_time = time.time()
            
            # Hikayeleri indir
            result = story_obj.story_download()
            
            # Sonuçları kontrol et
            if result and username in result and result[username].get('Story Data'):
                stories = result[username].get('Story Data', [])
                duration = time.time() - start_time
                
                # Geçici klasörden hedef klasöre dosyaları taşı
                temp_story_dir = temp_dir / "story" / username
                if temp_story_dir.exists():
                    # Profil klasörünü kopyala
                    profile_dir = temp_story_dir / "profile"
                    if profile_dir.exists():
                        shutil.copytree(profile_dir, user_dir / "profile", dirs_exist_ok=True)
                    
                    # JSON dosyalarını kopyala
                    for json_file in temp_story_dir.glob("*.json"):
                        shutil.copy(json_file, user_dir)
                    
                    # İndirilen ve yeni eklenen hikaye sayılarını tut
                    new_stories_count = 0
                    skipped_stories_count = 0
                    
                    # Hikaye medyalarını kopyala (MP4, PNG, JPG)
                    for media_file in temp_story_dir.glob("*.*"):
                        if media_file.suffix.lower() in [".mp4", ".png", ".jpg", ".jpeg"]:
                            # Dosya adı formatı: {zaman damgası}_{medya ID}.{uzantı}
                            # Yeni dosya adı: {kullanıcı adı}_story_{medya ID}_{zaman damgası}.{uzantı}
                            
                            # Medya ID ve zaman bilgisini ayıkla
                            original_filename = media_file.stem
                            parts = original_filename.split('_')
                            media_id = parts[-1] if len(parts) > 1 else original_filename
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            
                            new_filename = f"{username}_story_{media_id}_{timestamp}{media_file.suffix}"
                            target_path = user_dir / new_filename
                            
                            # Dosyanın önceden indirilip indirilmediğini kontrol et
                            # Aynı medya ID'sine sahip bir dosya var mı?
                            existing_files = list(user_dir.glob(f"{username}_story_{media_id}_*"))
                            
                            if existing_files:
                                # Bu medya ID'si daha önce indirilmiş, atla
                                skipped_stories_count += 1
                                continue
                            else:
                                # Yeni dosya, kopyala
                                shutil.copy(media_file, target_path)
                                new_stories_count += 1
                
                # Geçici klasörü temizle
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                # Sonuçları göster
                if new_stories_count > 0:
                    print(self._("stories_success", username, new_stories_count, duration))
                    
                    # İndirilen hikayelerin detaylarını göster
                    story_count = 0
                    for i, story in enumerate(stories[:new_stories_count], 1):
                        story_type = self._("media_video") if story.get('is_video') else self._("media_image")
                        story_time = story.get('taken_at_formatted', self._("unknown_time"))
                        print(self._("story_item", i, story_type, story_time))
                    
                    print(self._("stories_saved", user_dir))
                
                if skipped_stories_count > 0:
                    print(f"⚠️ {skipped_stories_count} hikaye daha önce indirildiği için atlandı.")
                
                if new_stories_count == 0 and skipped_stories_count > 0:
                    print(f"ℹ️ Tüm hikayeler ({skipped_stories_count}) zaten indirilmiş. Yeni hikaye yok.")
                
                return new_stories_count > 0
            else:
                # Geçici klasörü temizle
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(self._("stories_not_found", username))
                return False
                
        except Exception as e:
            # Geçici klasörü temizle
            shutil.rmtree(Path("./temp_story"), ignore_errors=True)
            print(self._("story_error", str(e)))
            return False
    
    def download_profile_pic(self, username):
        """Belirtilen kullanıcının profil resmini doğrudan indir."""
        try:
            # Kullanıcı klasörünü oluştur
            user_dir = self.content_types["profiles"] / username
            user_dir.mkdir(exist_ok=True)
            
            # İndirme başlangıcını göster
            print(self._("downloading_profile", username))
            
            # Instagram'dan profil sayfasını çek
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(f"https://www.instagram.com/{username}/", headers=headers, cookies=self.cookies)
            
            if response.status_code == 200:
                # Profil resmini bul
                profile_pic_match = re.search(r'"profile_pic_url":"([^"]+)"', response.text)
                profile_pic_match_hd = re.search(r'"profile_pic_url_hd":"([^"]+)"', response.text)
                
                # Yüksek çözünürlüklü versiyonu varsa onu al, yoksa normal versiyonu al
                if profile_pic_match_hd:
                    profile_pic_url = profile_pic_match_hd.group(1).replace('\\u0026', '&')
                elif profile_pic_match:
                    profile_pic_url = profile_pic_match.group(1).replace('\\u0026', '&')
                else:
                    print(self._("profile_not_found", username))
                    return False
                
                # Profil resmini indir
                img_response = requests.get(profile_pic_url)
                if img_response.status_code == 200:
                    # Resmi kaydet
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    img_path = user_dir / f"{username}_profile_{timestamp}.jpg"
                    
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    print(self._("profile_success", username))
                    print(self._("profile_saved", img_path))
                    return True
                else:
                    print(self._("profile_download_error", img_response.status_code))
                    return False
            else:
                print(self._("user_not_found", username, response.status_code))
                return False
                
        except Exception as e:
            print(self._("profile_error", str(e)))
            return False
    
    def list_downloaded_files(self):
        """İndirilen tüm dosyaları listele."""
        print(self._("downloads_title"))
        total_found = 0
        
        # Hikayeleri listele
        story_users = [d.name for d in self.content_types["stories"].glob("*") if d.is_dir()]
        if story_users:
            print(self._("downloads_stories"))
            for username in story_users:
                story_count = len(list(self.content_types["stories"].glob(f"{username}/*.mp4"))) + \
                              len(list(self.content_types["stories"].glob(f"{username}/*.png"))) + \
                              len(list(self.content_types["stories"].glob(f"{username}/*.jpg")))
                print(self._("downloads_item", username, story_count, self._("downloads_media")))
                total_found += 1
        
        # Gönderileri listele
        post_users = [d.name for d in self.content_types["posts"].glob("*") if d.is_dir()]
        if post_users:
            print(self._("downloads_posts"))
            for username in post_users:
                post_dirs = list(self.content_types["posts"].glob(f"{username}/*"))
                post_count = len([d for d in post_dirs if d.is_dir()])
                print(self._("downloads_item", username, post_count, self._("downloads_post")))
                total_found += 1
        
        # Profil resimlerini listele
        profile_users = [d.name for d in self.content_types["profiles"].glob("*") if d.is_dir()]
        if profile_users:
            print(self._("downloads_profiles"))
            for username in profile_users:
                profile_count = len(list(self.content_types["profiles"].glob(f"{username}/*.jpg")))
                print(self._("downloads_item", username, profile_count, self._("downloads_image")))
                total_found += 1
        
        if total_found == 0:
            print(self._("downloads_empty"))
            return False
        
        return True

    def batch_download(self, username):
        """Belirli bir kullanıcının birden fazla içeriğini toplu olarak indirir."""
        if not self.cookies:
            print(self._("no_cookies"))
            if not self.get_interactive_cookies():
                return False
        
        try:
            # İndirme seçeneklerini göster
            print(self._("batch_options"))
            print(self._("batch_option_stories"))
            print(self._("batch_option_posts"))
            print(self._("batch_option_both"))
            
            choice = input(self._("batch_option_choice")).strip()
            
            print(self._("batch_download_start", username))
            
            success = True
            
            # Hikayeleri indir
            if choice in ["1", "3"]:
                success = self.download_story(username) and success
            
            # Son gönderileri indir
            if choice in ["2", "3"]:
                success = self.download_recent_posts(username) and success
            
            if success:
                print(self._("batch_download_complete"))
                return True
            return False
            
        except Exception as e:
            print(self._("batch_download_error", str(e)))
            return False
    
    def download_recent_posts(self, username, limit=12):
        """Bir kullanıcının son gönderilerini indirir."""
        try:
            # Kullanıcı klasörünü oluştur
            user_dir = self.content_types["posts"] / username
            user_dir.mkdir(exist_ok=True)
            
            # Kullanıcının son gönderilerini al
            feed_obj = InstaFeed()
            feed_obj.cookies = self.cookies
            feed_obj.username = username
            feed_obj.limit = limit  # Son 12 gönderi
            
            print(self._("downloading_posts", username, limit))
            start_time = time.time()
            
            # Gönderileri al
            results = feed_obj.feed_download()
            
            if results and username in results and results[username].get('Media Data'):
                post_codes = results[username].get('Media Data', [])
                
                if not post_codes:
                    print(self._("no_posts_found", username))
                    return False
                
                # Her gönderiyi indir
                success_count = 0
                skipped_count = 0
                
                for post_code in post_codes:
                    # Gönderi daha önce indirilmiş mi kontrol et
                    post_dir = user_dir / post_code
                    if post_dir.exists():
                        print(f"⚠️ Gönderi atlandı (daha önce indirilmiş): {post_code}")
                        skipped_count += 1
                        continue
                    
                    print(self._("downloading_post", post_code))
                    if self.download_post(post_code):
                        success_count += 1
                
                duration = time.time() - start_time
                
                if success_count > 0:
                    print(self._("posts_success", username, success_count, len(post_codes), duration))
                
                if skipped_count > 0:
                    print(f"ℹ️ {skipped_count}/{len(post_codes)} gönderi daha önce indirildiği için atlandı.")
                
                if success_count == 0 and skipped_count > 0:
                    print(f"ℹ️ Tüm gönderiler ({skipped_count}) zaten indirilmiş. Yeni gönderi yok.")
                
                return success_count > 0
            else:
                print(self._("posts_not_found", username))
                return False
                
        except Exception as e:
            print(self._("post_error", str(e)))
            return False

    def download_highlights(self, username):
        """Download highlights for a user."""
        if not self.cookies:
            print(self._("no_cookies"))
            if not self.get_interactive_cookies():
                return False
        

    def download_post(self, post_url):
        """Belirtilen gönderiyi indir."""
        try:
            # Post kodunu URL'den çıkar
            post_code = None
            
            # URL formatını kontrol et
            url_patterns = [
                r'instagram.com/p/([^/]+)',
                r'instagram.com/reel/([^/]+)',
                r'instagram.com/tv/([^/]+)'
            ]
            
            for pattern in url_patterns:
                match = re.search(pattern, post_url)
                if match:
                    post_code = match.group(1)
                    break
            
            # Eğer kod bulunamazsa URL'yi doğrudan kod olarak kullan
            if not post_code:
                post_code = post_url.strip()
            
            # URL parametrelerini temizle
            if '?' in post_code:
                post_code = post_code.split('?')[0]
                
            # Geçerliliği kontrol et
            if not post_code or len(post_code) < 5:
                print(self._("invalid_post"))
                return False
            
            # İndirme başlangıcını kaydet
            start_time = time.time()
            
            # İndirme klasörünü oluştur
            temp_dir = Path(tempfile.mkdtemp())
            
            # Instagram'ın 2024 API değişiklikleri için optimize edilmiş başlıklar
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.instagram.com/",
                "sec-ch-ua": "\"Chromium\";v=\"124\", \"Google Chrome\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\""
            }
            
            # Çalışan bir çerez kontrolü yap
            if not self.cookies or not self.cookies.get('sessionid'):
                print("⚠️ Instagram oturum çerezi (sessionid) bulunamadı. Çerezleri ayarlamanız gerekebilir.")
                if self.get_interactive_cookies():
                    print("✅ Çerezler başarıyla ayarlandı. İndirme devam ediyor...")
                else:
                    print("❌ Çerezler ayarlanamadı. İndirme başarısız olabilir.")
            
            # Instagram'ın Yeni API Formatları (2024) için çerez tabanlı doğrulama
            combined_url = f"https://www.instagram.com/p/{post_code}/"
            post_data = None
            graphql_username = None
            
            print(f"📥 Gönderi indiriliyor: {post_code}")
            
            try:
                # Gönderi sayfasını çek
                response = requests.get(combined_url, headers=headers, cookies=self.cookies, allow_redirects=True)
                html_content = None
                
                if response.status_code == 200:
                    # Print response headers for debugging
                    print(f"📋 Response Headers:")
                    for key, value in response.headers.items():
                        print(f"    {key}: {value}")
                    
                    # Save the raw binary response first
                    with open("instapost_raw.bin", "wb") as f:
                        f.write(response.content)
                    print(f"💾 Raw binary response saved to 'instapost_raw.bin'")
                    
                    try:
                        # Check if content is compressed
                        content_encoding = response.headers.get('Content-Encoding', '').lower()
                        if 'gzip' in content_encoding:
                            html_content = gzip.decompress(response.content).decode('utf-8')
                        elif 'br' in content_encoding:
                            html_content = brotli.decompress(response.content).decode('utf-8')
                        else:
                            html_content = response.text
                    except Exception as e:
                        print(f"⚠️ Decompression error: {str(e)}")
                        # Fallback - try direct download as separate request without compression
                        try:
                            print("🔄 Using fallback method - direct download without compression...")
                            # Create new headers without accepting compression
                            fallback_headers = headers.copy()
                            fallback_headers["Accept-Encoding"] = "identity"
                            fallback_response = requests.get(combined_url, headers=fallback_headers, cookies=self.cookies)
                            html_content = fallback_response.text
                            print(f"✅ Fallback method successful")
                        except Exception as fallback_error:
                            print(f"❌ Fallback method failed: {str(fallback_error)}")
                            # Last resort - try to directly download the page using a tool like curl
                            try:
                                import subprocess
                                print("🔄 Using system curl as last resort...")
                                # Create a temporary cookie file
                                cookie_file = "temp_cookies.txt"
                                with open(cookie_file, "w") as f:
                                    for cookie_name, cookie_value in self.cookies.items():
                                        f.write(f"instagram.com\tTRUE\t/\tTRUE\t0\t{cookie_name}\t{cookie_value}\n")
                                    
                                    # Use curl with the cookie file
                                    curl_cmd = [
                                        "curl", "-L", 
                                        "-A", headers["User-Agent"], 
                                        "-b", cookie_file,
                                        combined_url, 
                                        "-o", "instapost.html"
                                    ]
                                    subprocess.run(curl_cmd, check=True)
                                    
                                    # Clean up temporary cookie file
                                    try:
                                        os.remove(cookie_file)
                                    except:
                                        pass
                                        
                                    with open("instapost.html", "r", encoding="utf-8") as f:
                                        html_content = f.read()
                                    print(f"✅ Direct download with curl successful")
                            except Exception as curl_error:
                                print(f"❌ System curl failed: {str(curl_error)}")
                                return False
                    
                    print(f"✅ Bağlantı başarılı: {combined_url}")
                    
                    # Debug: Save HTML content to file for analysis
                    with open("instapost.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print(f"💾 HTML içeriği 'instapost.html' dosyasına kaydedildi")
                else:
                    # Reel URL'sini dene
                    reel_url = f"https://www.instagram.com/reel/{post_code}/"
                    try:
                        reel_response = requests.get(reel_url, headers=headers, cookies=self.cookies, allow_redirects=True)
                        if reel_response.status_code == 200:
                            # Print response headers for debugging
                            print(f"📋 Reel Response Headers:")
                            for key, value in reel_response.headers.items():
                                print(f"    {key}: {value}")
                            
                            # Save the raw binary response first
                            with open("instapost_reel_raw.bin", "wb") as f:
                                f.write(reel_response.content)
                            print(f"💾 Raw binary response saved to 'instapost_reel_raw.bin'")
                            
                            try:
                                # Check if content is compressed
                                content_encoding = reel_response.headers.get('Content-Encoding', '').lower()
                                if 'gzip' in content_encoding:
                                    html_content = gzip.decompress(reel_response.content).decode('utf-8')
                                elif 'br' in content_encoding:
                                    html_content = brotli.decompress(reel_response.content).decode('utf-8')
                                else:
                                    html_content = reel_response.text
                            except Exception as e:
                                print(f"⚠️ Decompression error: {str(e)}")
                                # Fallback - try direct download as separate request without compression
                                try:
                                    print("🔄 Using fallback method - direct download without compression...")
                                    # Create new headers without accepting compression
                                    fallback_headers = headers.copy()
                                    fallback_headers["Accept-Encoding"] = "identity"
                                    fallback_response = requests.get(reel_url, headers=fallback_headers, cookies=self.cookies)
                                    html_content = fallback_response.text
                                    print(f"✅ Fallback method successful")
                                except Exception as fallback_error:
                                    print(f"❌ Fallback method failed: {str(fallback_error)}")
                                    # Last resort - try to directly download the page using a tool like curl
                                    try:
                                        import subprocess
                                        print("🔄 Using system curl as last resort...")
                                        # Create a temporary cookie file
                                        cookie_file = "temp_cookies.txt"
                                        with open(cookie_file, "w") as f:
                                            for cookie_name, cookie_value in self.cookies.items():
                                                f.write(f"instagram.com\tTRUE\t/\tTRUE\t0\t{cookie_name}\t{cookie_value}\n")
                                        
                                        # Use curl with the cookie file
                                        curl_cmd = [
                                            "curl", "-L", 
                                            "-A", headers["User-Agent"], 
                                            "-b", cookie_file,
                                            reel_url, 
                                            "-o", "instapost.html"
                                        ]
                                        subprocess.run(curl_cmd, check=True)
                                        
                                        # Clean up temporary cookie file
                                        try:
                                            os.remove(cookie_file)
                                        except:
                                            pass
                                            
                                        with open("instapost.html", "r", encoding="utf-8") as f:
                                            html_content = f.read()
                                        print(f"✅ Direct download with curl successful")
                                    except Exception as curl_error:
                                        print(f"❌ System curl failed: {str(curl_error)}")
                                        return False
                                
                            print(f"✅ Bağlantı başarılı: {reel_url}")
                            
                            # Debug: Save HTML content to file for analysis
                            with open("instapost.html", "w", encoding="utf-8") as f:
                                f.write(html_content)
                            print(f"💾 HTML içeriği 'instapost.html' dosyasına kaydedildi")
                        else:
                            print(f"❌ Gönderi sayfasına erişilemedi: {response.status_code}, Reel: {reel_response.status_code}")
                    except Exception as e:
                        print(f"❌ Reel sayfasına erişim hatası: {str(e)}")
                
                if not html_content:
                    print("❌ Gönderi sayfasına erişilemedi.")
                    return False
                
                # Kullanıcı adını bulmak için geliştirilmiş regex kalıpları
                username_patterns = [
                    # Instagram 2024 için yeni kalıplar
                    r'property="og:title"\s+content="([^"]*?) on Instagram"',
                    r'property="og:title"\s+content="Instagram post by ([^"]*?)"',
                    r'property="og:description"\s+content="([^"]*?) shared a post on Instagram"',
                    r'property="og:description"\s+content="([^"]*?) on Instagram: "',
                    # Schema.org yapıları
                    r'"alternateName"\s*:\s*"@([^"]+)"',
                    # React yapısı
                    r'"username"\s*:\s*"([^"]+)"',
                    # Profil linkleri
                    r'href="https://www\.instagram\.com/([^/]+)/"[^>]*>',
                    r'href="/([^/]+)/"[^>]*>@[^<]+</a>',
                    # Basit metin arama
                    r'"@([a-zA-Z0-9._]{3,30})"',
                ]
                
                # Kullanıcı adını bul
                for pattern in username_patterns:
                    match = re.search(pattern, html_content)
                    if match:
                        username_candidate = match.group(1).strip()
                        # Kullanıcı adı temizleme ve doğrulama
                        if username_candidate and len(username_candidate) > 2 and not any(x in username_candidate for x in ['Instagram', 'http', 'login', 'sign up']):
                            graphql_username = username_candidate
                            print(f"✅ Kullanıcı adı bulundu: {graphql_username}")
                            break
                
                # Eğer kullanıcı adını bulamazsak, özel bir post kodu oluştur
                if not graphql_username:
                    # React veri yapısını kullanarak dene
                    print("🔍 React veri yapısını kontrol ediliyor...")
                    shared_data_match = re.search(r'window\._sharedData\s*=\s*({.*?});</script>', html_content, re.DOTALL)
                    if shared_data_match:
                        try:
                            shared_data = json.loads(shared_data_match.group(1))
                            print(f"✅ SharedData JSON başarıyla ayrıştırıldı")
                            if "entry_data" in shared_data:
                                print(f"✅ entry_data bulundu")
                                if "PostPage" in shared_data["entry_data"]:
                                    print(f"✅ PostPage bulundu")
                                    post_page = shared_data["entry_data"]["PostPage"][0]
                                    if "graphql" in post_page and "shortcode_media" in post_page["graphql"]:
                                        print(f"✅ graphql ve shortcode_media bulundu")
                                        media = post_page["graphql"]["shortcode_media"]
                                        if "owner" in media and "username" in media["owner"]:
                                            graphql_username = media["owner"]["username"]
                                            print(f"✅ SharedData'dan kullanıcı adı bulundu: {graphql_username}")
                        except Exception as e:
                            print(f"⚠️ SharedData işleme hatası: {str(e)}")
                
                # AdditionalData formatını dene
                print("🔍 Additional data kontrol ediliyor...")
                additional_data_match = re.search(r'window\.__additionalDataLoaded\s*\(\s*[\'"]feed[\'"]\s*,\s*({.*?})\);</script>', html_content, re.DOTALL)
                if additional_data_match:
                    try:
                        additional_data = json.loads(additional_data_match.group(1))
                        print(f"✅ AdditionalData JSON başarıyla ayrıştırıldı")
                        # ... process additional data
                    except Exception as e:
                        print(f"⚠️ AdditionalData işleme hatası: {str(e)}")

                # Alternatif olarak app-state de kontrol et
                print("🔍 Server app state kontrol ediliyor...")
                app_state_match = re.search(r'<script type="application/json" id="server-app-state">(.*?)</script>', html_content, re.DOTALL)
                if app_state_match:
                    try:
                        app_state = json.loads(app_state_match.group(1))
                        print(f"✅ App state JSON başarıyla ayrıştırıldı")
                        # ... process app state
                    except Exception as e:
                        print(f"⚠️ App state işleme hatası: {str(e)}")

                # React veri yapısını kontrol et (2024 Yeni Format)
                print("🔍 React JSON veri yapılarını kontrol ediliyor...")
                react_data_patterns = [
                    r'<script type="application/json" data-sjs>[^<]*({"require":\[.*?\]})</script>',
                    r'<script type="application/json" id="server-app-state">(.*?)</script>',
                    r'<script type="application/json"[^>]*>({".*?})</script>'
                ]
                
                react_images = []
                react_videos = []
                
                for pattern in react_data_patterns:
                    matches = re.findall(pattern, html_content, re.DOTALL)
                    if matches:
                        for match_data in matches:
                            try:
                                # JSON verisini ayıkla ve işle
                                json_data = json.loads(match_data)
                                print(f"✅ React JSON verisi başarıyla ayrıştırıldı")
                                
                                # JSON'da medya URL'lerini ara
                                json_str = json.dumps(json_data)
                                
                                # Medya URL'lerini topla
                                img_urls = re.findall(r'"(?:display_url|profile_pic_url|profile_pic_url_hd|thumbnail_src|optimized_image_url|static_image|uri)":\s*"(https:[^"]+\.(jpg|jpeg|png)[^"]*)"', json_str)
                                vid_urls = re.findall(r'"(?:video_url|contentUrl|playback_url|uri)":\s*"(https:[^"]+\.(mp4|mov)[^"]*)"', json_str)
                                
                                # URL'leri listelere ekle
                                for url_match in img_urls:
                                    if isinstance(url_match, tuple):
                                        react_images.append(url_match[0].replace('\\u0026', '&'))
                                
                                for url_match in vid_urls:
                                    if isinstance(url_match, tuple):
                                        react_videos.append(url_match[0].replace('\\u0026', '&'))
                                
                                # Kullanıcı adını bulmayı dene
                                if not graphql_username:
                                    username_match = re.search(r'"username":\s*"([^"]+)"', json_str)
                                    if username_match:
                                        potential_username = username_match.group(1)
                                        if potential_username and len(potential_username) > 2:
                                            graphql_username = potential_username
                                            print(f"✅ React verisinden kullanıcı adı bulundu: {graphql_username}")
                            except Exception as e:
                                print(f"⚠️ React JSON işleme hatası: {str(e)}")

                # Hala bulamadıysak, kullanıcı ID'si üzerinden deneyelim
                if not graphql_username:
                    print("🔍 User ID'yi kontrol ediliyor...")
                    user_id_patterns = [
                        r'"owner_id":\s*"(\d+)"',
                        r'"user_id":\s*"(\d+)"',
                        r'"profile_id":\s*"(\d+)"',
                        r'"profilePage_(\d+)"',
                    ]
                    
                    for pattern in user_id_patterns:
                        matches = re.findall(pattern, html_content)
                        if matches:
                            print(f"✅ Eşleşen ID'ler bulundu: {matches[:5]}")
                            # ID'ler listesindeki her ID'yi dene
                            for user_id in matches:
                                try:
                                    api_url = f"https://www.instagram.com/graphql/query/?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables=%7B%22user_id%22%3A%22{user_id}%22%2C%22include_reel%22%3Atrue%7D"
                                    api_headers = headers.copy()
                                    api_headers["X-Requested-With"] = "XMLHttpRequest"
                                    api_response = requests.get(api_url, headers=api_headers, cookies=self.cookies)
                                    
                                    if api_response.status_code == 200:
                                        api_data = api_response.json()
                                        if "data" in api_data and "user" in api_data["data"] and api_data["data"]["user"]:
                                            graphql_username = api_data["data"]["user"]["username"]
                                            print(f"✅ ID {user_id} ile kullanıcı adı bulundu: {graphql_username}")
                                            break
                                except Exception as e:
                                    print(f"⚠️ ID {user_id} ile kullanıcı adı sorgulama hatası: {str(e)}")
                                    continue
                            
                            if graphql_username:
                                break

                # Son çare - meta etiketlerinden post verisi ekstra
                if not post_data:
                    print("🔍 Meta etiketlerinden veri çıkarılıyor...")
                    # Meta etiketlerindeki resim ve video URL'lerini bul
                    image_url = None
                    video_url = None
                    
                    # og:image
                    image_match = re.search(r'property="og:image"\s+content="([^"]+)"', html_content)
                    if image_match:
                        image_url = image_match.group(1)
                        print(f"✅ og:image bulundu: {image_url}")
                    
                    # og:video
                    video_match = re.search(r'property="og:video"\s+content="([^"]+)"', html_content)
                    if video_match:
                        video_url = video_match.group(1)
                        print(f"✅ og:video bulundu: {video_url}")
                    
                    if image_url or video_url:
                        post_data = {
                            "direct_images": [image_url] if image_url else [],
                            "direct_videos": [video_url] if video_url else []
                        }
                        print(f"✅ Meta etiketlerinden medya URL'leri bulundu")
                
                # Direct media URL pattern check
                print("🔍 Direkt medya URL'leri kontrol ediliyor...")
                
                # Instagram post ve medya URL'leri için gelişmiş arama
                # Instagram'ın yüksek çözünürlüklü resim URL'leri genellikle bu deseni izler
                media_urls_images = re.findall(r'https://[^"\s]+\.cdninstagram\.com/[^"\s]+/t51\.[^"\s]+\d+_n\.jpg[^"\s]*', html_content)
                
                if not media_urls_images:
                    # Alternatif URL desenleri
                    media_urls_images = re.findall(r'https://[^"\s]+\.cdninstagram\.com/[^"\s]+/e35/[^"\s]+\.jpg[^"\s]*', html_content)
                
                if not media_urls_images:
                    # Genel URL deseni
                    media_urls_images = re.findall(r'https://[^"\s]+\.cdninstagram\.com/[^"\s]+\.jpg[^"\s]*', html_content)
                
                # Video URL'leri için özel arama
                media_urls_videos = re.findall(r'https://[^"\s]+\.cdninstagram\.com/[^"\s]+\.mp4[^"\s]*', html_content)
                
                # Profil resimlerini filtrele
                filtered_images = []
                for img_url in media_urls_images:
                    # Profil fotoğraflarına özgü URL parçaları
                    if not any(pattern in img_url.lower() for pattern in [
                        "profile_pic", 
                        "/p/p", 
                        "/pp/",
                        "/profiles/",
                        "_profile_",
                        "profilepics",
                        "s150x150",
                        "s320x320"
                    ]):
                        # Instagram post resimlerinin desenleri
                        if any(pattern in img_url for pattern in [
                            "t51.", 
                            "/e35/", 
                            "_n.jpg", 
                            "_e35_",
                            "_e15_",
                            "s1080x1080",
                            "s1080x607",
                            "s640x640",
                            "s720x720"
                        ]):
                            filtered_images.append(img_url)
                
                # Filtrelenmiş sonuçları kullan
                media_urls_images = filtered_images

                # Carousel/Sidecar kontrolü için ek tarama
                print("🔍 Carousel gönderisi kontrolü yapılıyor...")
                carousel_patterns = [
                    r'"edge_sidecar_to_children":\s*{"edges":\s*\[(.*?)\]\s*}',
                    r'"carousel_media":\s*\[(.*?)\]',
                    r'"carousel":\s*\[(.*?)\]'
                ]
                
                carousel_images = []
                carousel_videos = []
                
                for pattern in carousel_patterns:
                    carousel_matches = re.findall(pattern, html_content, re.DOTALL)
                    if carousel_matches:
                        print(f"✅ Carousel yapısı tespit edildi")
                        for carousel_data in carousel_matches:
                            # Carousel içindeki görüntü URL'lerini bul
                            carousel_imgs = re.findall(r'"display_url":"([^"]+)"', carousel_data)
                            carousel_vids = re.findall(r'"video_url":"([^"]+)"', carousel_data)
                            
                            carousel_images.extend([url.replace('\\u0026', '&') for url in carousel_imgs])
                            carousel_videos.extend([url.replace('\\u0026', '&') for url in carousel_vids])
                            
                            print(f"✅ Carousel'den {len(carousel_imgs)} resim, {len(carousel_vids)} video URL'si eklendi")

                all_image_urls = []
                all_video_urls = []
                
                # React JSON'dan bulunan URL'leri ekle
                all_image_urls.extend(react_images)
                all_video_urls.extend(react_videos)
                
                # Bulunan diğer medya URL'lerini ekle
                all_image_urls.extend(media_urls_images)
                all_video_urls.extend(media_urls_videos)
                
                # Carousel resimlerini ve videolarını ekle
                all_image_urls.extend(carousel_images)
                all_video_urls.extend(carousel_videos)
                
                if media_urls_images or media_urls_videos or carousel_images or carousel_videos or react_images or react_videos:
                    post_data = {
                        "direct_images": media_urls_images + carousel_images + react_images,
                        "direct_videos": media_urls_videos + carousel_videos + react_videos
                    }
                    print(f"✅ HTML içeriğinden {len(media_urls_images)} resim, {len(media_urls_videos)} video URL'si bulundu")
                    print(f"✅ Carousel'den {len(carousel_images)} resim, {len(carousel_videos)} video URL'si bulundu")

                if post_data:
                    print(f"✅ Post verisi bulundu, indirme başlıyor...")
                else:
                    print(f"❌ Post verisi bulunamadı!")

                # Hala bulunamadıysa, varsayılan olarak postu indirelim
                if not graphql_username:
                    graphql_username = f"unknown_user_{int(time.time())}"
                    print(f"⚠️ Kullanıcı adı bulunamadı, geçici ad kullanılıyor: {graphql_username}")

                # Kullanıcı dizinini oluştur
                user_dir = self.content_types["posts"] / graphql_username
                user_dir.mkdir(exist_ok=True)
                
                # Gönderi klasörünü oluştur ve kontrol et
                post_dir = user_dir / post_code
                if post_dir.exists() and list(post_dir.glob("*.*")):
                    print(f"⚠️ Bu gönderi ({post_code}) daha önce indirilmiş. Tekrar indirilmiyor.")
                    print(f"📁 Gönderi dizini: {post_dir}")
                    return True
                
                # Gönderi klasörünü oluştur
                post_dir.mkdir(exist_ok=True)
                
                # Öncelikle og:image meta tag'inden resim indirmeyi dene - bu neredeyse her zaman mevcuttur
                download_successful = False
                og_image_match = re.search(r'<meta property="og:image" content="([^"]+)"', html_content)
                if og_image_match:
                    og_image_url = og_image_match.group(1).replace("&amp;", "&")
                    try:
                        print(f"🔍 Ana gönderi resmini indirme girişimi: {og_image_url}")
                        img_response = requests.get(og_image_url, headers=headers)
                        if img_response.status_code == 200 and len(img_response.content) > 5000:
                            img_path = post_dir / "post_main_image.jpg"
                            with open(img_path, "wb") as f:
                                f.write(img_response.content)
                            print(f"✅ Ana gönderi resmi başarıyla indirildi")
                            download_successful = True
                    except Exception as e:
                        print(f"❌ Ana gönderi resmi indirme hatası: {str(e)}")
                
                # HTML'den tüm olası medya URL'lerini çıkar
                all_image_patterns = [
                    r'<img[^>]*\ssrc="([^"]+\.(jpg|jpeg|png)[^"]*)"',
                    r'background-image:\s*url\([\'"]?([^\'"]*\.(jpg|jpeg|png))[\'"]?\)',
                    r'"display_url":"([^"]+)"',
                    r'"display_src":"([^"]+)"',
                    r'"url":"(https:[^"]+\.(jpg|jpeg|png)[^"]*)"',
                    r'content="([^"]+\.(jpg|jpeg|png)[^"]*)"',
                    # 2024 formatları için yeni kalıplar
                    r'"image_versions2":\s*{"candidates":\s*\[\s*{"url":\s*"([^"]+)"',
                    r'"optimized_image_url":\s*"([^"]+)"',
                    r'"static_image":\s*"([^"]+)"',
                    r'"image":\s*{"uri":\s*"([^"]+)"',
                ]
                
                all_video_patterns = [
                    r'<video[^>]*\ssrc="([^"]+)"',
                    r'<source[^>]*\ssrc="([^"]+\.(mp4|mov)[^"]*)"',
                    r'"video_url":"([^"]+)"',
                    r'"contentUrl":"([^"]+\.(mp4|mov)[^"]*)"',
                    r'"url":"(https:[^"]+\.(mp4|mov)[^"]*)"',
                    # 2024 formatları için yeni kalıplar
                    r'"video_versions":\s*\[\s*{"type":\s*\d+,\s*"url":\s*"([^"]+)"',
                    r'"playback_url":\s*"([^"]+)"',
                    r'"video":\s*{"uri":\s*"([^"]+)"',
                ]
                
                # Regex paternlerinden daha fazla URL çıkar
                for pattern in all_image_patterns:
                    matches = re.findall(pattern, html_content)
                    if matches:
                        for match in matches:
                            if isinstance(match, tuple):
                                all_image_urls.append(match[0])
                            else:
                                all_image_urls.append(match)
                
                # Tüm video URL'lerini topla
                for pattern in all_video_patterns:
                    matches = re.findall(pattern, html_content)
                    if matches:
                        for match in matches:
                            if isinstance(match, tuple):
                                all_video_urls.append(match[0])
                            else:
                                all_video_urls.append(match)
                
                # URL'leri temizle
                all_image_urls = [url.replace('\\u0026', '&').replace("&amp;", "&") for url in all_image_urls]
                all_video_urls = [url.replace('\\u0026', '&').replace("&amp;", "&") for url in all_video_urls]
                
                # Tekrarlananları kaldır
                all_image_urls = list(set(all_image_urls))
                all_video_urls = list(set(all_video_urls))
                
                # Geçersiz URL'leri filtrele
                all_image_urls = [url for url in all_image_urls if url.startswith(('http://', 'https://')) and len(url) > 20]
                all_video_urls = [url for url in all_video_urls if url.startswith(('http://', 'https://')) and len(url) > 20]
                
                # Post resimlerini profil resimlerinden ayırt etmek için filtrele
                post_image_urls = []
                for img_url in all_image_urls:
                    # Profil fotoğraflarına özgü URL parçaları
                    if not any(pattern in img_url.lower() for pattern in [
                        "profile_pic", 
                        "/p/p", 
                        "/pp/",
                        "/profiles/",
                        "_profile_",
                        "s150x150",
                        "s320x320"
                    ]) and any(pattern in img_url for pattern in [
                        "cdninstagram",
                        "fbcdn",
                        "t51.", 
                        "_n.jpg", 
                        "_e35",
                        "s1080x1080",
                        "s640x640",
                        "s720x720"
                    ]):
                        post_image_urls.append(img_url)
                
                # En büyük resimler için Instagram CDN URL'lerini seç
                instagram_cdn_urls = [url for url in post_image_urls if 'cdninstagram.com' in url or 'fbcdn.net' in url]
                if instagram_cdn_urls:
                    all_image_urls = instagram_cdn_urls
                
                # Tüm bulunan URL'leri post_data'ya ekle
                if all_image_urls or all_video_urls:
                    if not post_data:
                        post_data = {}
                    
                    # Ana og:image'i her zaman direkt resim listesinin başına ekle
                    direct_images = []
                    if og_image_match:
                        og_image_url = og_image_match.group(1).replace("&amp;", "&")
                        if og_image_url not in direct_images:
                            direct_images.append(og_image_url)
                    
                    # Diğer bulunan post resimlerini ekle
                    direct_images.extend([url for url in post_image_urls if url not in direct_images])
                    
                    # Carousel resimlerini ekle
                    for url in carousel_images:
                        clean_url = url.replace("\\u0026", "&").replace("&amp;", "&")
                        if clean_url not in direct_images:
                            direct_images.append(clean_url)
                    
                    post_data["direct_images"] = direct_images
                    post_data["direct_videos"] = list(set(post_data.get("direct_videos", []) + all_video_urls + carousel_videos))
                    
                    print(f"✅ Regex paternlerinden {len(all_image_urls)} resim, {len(all_video_urls)} video URL'si bulundu")
                    print(f"✅ Filtreleme sonrası {len(direct_images)} gerçek post içeriği bulundu")
                
                if download_successful:
                    duration = time.time() - start_time
                    print(self._("post_success", graphql_username, duration))
                    print(self._("post_saved", post_dir))
                    return True
                
                # İndirme işlemini gerçekleştir
                download_successful = False
                
                if post_data:
                    # Resimleri indir
                    if "direct_images" in post_data and post_data["direct_images"]:
                        # URL'leri göster
                        if len(post_data["direct_images"]) > 0:
                            print(f"🔍 İndirmeye hazır post resimleri:")
                            for i, url in enumerate(post_data["direct_images"][:3]):
                                print(f"  {i+1}. {url[:70]}...")
                            if len(post_data["direct_images"]) > 3:
                                print(f"  ...ve {len(post_data['direct_images']) - 3} resim daha")
                        
                        # Her resmi indir
                        for i, img_url in enumerate(post_data["direct_images"]):
                            try:
                                img_response = requests.get(img_url, headers=headers)
                                if img_response.status_code == 200 and len(img_response.content) > 5000:  # Minimum boyut kontrolü
                                    img_path = post_dir / f"image_{i+1}.jpg"
                                    with open(img_path, "wb") as f:
                                        f.write(img_response.content)
                                    print(f"✅ Resim {i+1} indirildi ({len(img_response.content)/1024:.1f} KB)")
                                    download_successful = True
                            except Exception as e:
                                print(f"❌ Resim {i+1} indirilemedi: {str(e)}")
                    
                    # Videoları indir
                    if "direct_videos" in post_data and post_data["direct_videos"]:
                        for i, vid_url in enumerate(post_data["direct_videos"]):
                            try:
                                vid_response = requests.get(vid_url, headers=headers)
                                if vid_response.status_code == 200 and len(vid_response.content) > 10000:  # Minimum boyut kontrolü
                                    vid_path = post_dir / f"video_{i+1}.mp4"
                                    with open(vid_path, "wb") as f:
                                        f.write(vid_response.content)
                                    print(f"✅ Video {i+1} indirildi ({len(vid_response.content)/1024/1024:.1f} MB)")
                                    download_successful = True
                            except Exception as e:
                                print(f"❌ Video {i+1} indirilemedi: {str(e)}")
                
                # İndirme başarılı mı kontrol et
                if download_successful:
                    duration = time.time() - start_time
                    print(self._("post_success", graphql_username, duration))
                    print(self._("post_saved", post_dir))
                    return True
                
                # İndirme başarısız olduysa ve post_dir boşsa sil
                if post_dir.exists() and not any(post_dir.glob("*.*")):
                    try:
                        shutil.rmtree(post_dir)
                    except Exception:
                        pass
                
                print(self._("post_fail"))
                return False
            
            except Exception as e:
                print(f"❌ Veri alımı hatası: {str(e)}")
                return False
                
        except Exception as e:
            print(f"❌ Post indirme hatası: {str(e)}")
            traceback.print_exc()
            return False
        finally:
            # Her durumda geçici klasörü temizle
            try:
                if 'temp_dir' in locals() and temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def show_menu(self):
        """Ana menüyü göster."""
        print(self._("app_title"))
        while True:
            try:
                print("\n" + self._("app_name"))
                print(self._("menu_download_story"))
                print(self._("menu_download_post"))
                print(self._("menu_download_profile"))
                print(self._("menu_batch_download"))
                print(self._("menu_set_cookies"))
                print(self._("menu_list_downloads"))
                print(self._("menu_clean"))
                print(self._("menu_lang"))
                print(self._("menu_exit"))
                
                choice = input(self._("menu_choice")).strip()
                
                if choice == "1":
                    username = input(self._("username_prompt")).strip()
                    if username:
                        self.download_story(username)
                
                elif choice == "2":
                    post_url = input(self._("post_url_prompt")).strip()
                    if post_url:
                        self.download_post(post_url)
                
                elif choice == "3":
                    username = input(self._("username_prompt")).strip()
                    if username:
                        self.download_profile_pic(username)
                
                elif choice == "4":
                    username = input(self._("batch_username_prompt")).strip()
                    if username:
                        self.batch_download(username)
                
                elif choice == "5":
                    self.get_interactive_cookies()
                
                elif choice == "6":
                    self.list_downloaded_files()
                
                elif choice == "7":
                    confirm = input(self._("clean_confirm")).strip().lower()
                    if confirm == self._("yes_short"):
                        # Tüm içerik klasörlerini temizle
                        for folder in self.content_types.values():
                            shutil.rmtree(folder, ignore_errors=True)
                            folder.mkdir(exist_ok=True)
                        print(self._("clean_success"))
                    else:
                        print(self._("clean_cancel"))
                
                elif choice == "8":
                    self.change_language()
                
                elif choice == "9":
                    print(self._("exit_message"))
                    break
                
                else:
                    print(self._("invalid_choice"))
            
            except KeyboardInterrupt:
                print(self._("interrupt_message"))
                break
            
            except Exception as e:
                print(self._("unexpected_error", str(e)))


# Ana uygulamayı başlat
if __name__ == "__main__":
    stalker = InstaStalker()
    stalker.show_menu()

