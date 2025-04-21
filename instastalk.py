#!/usr/bin/env python3
import os
import json
import getpass
import time
import re
import requests
import shutil
from datetime import datetime
from pathlib import Path
import gzip
import brotli
import traceback
import tempfile
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
        "menu_choice": "\nSeçiminiz (1-10): ",
        "story_username_prompt": "Hikayeleri indirilecek kullanıcı adı: ",
        "post_url_prompt": "Gönderi veya reel URL'si: ",
        "profile_username_prompt": "Profil resmi indirilecek kullanıcı adı: ",
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
        "menu_choice": "\nYour choice (1-10): ",
        "story_username_prompt": "Username for stories to download: ",
        "post_url_prompt": "Post or reel URL: ",
        "profile_username_prompt": "Username for profile picture to download: ",
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
    
    def show_menu(self):
        """Only allow story download."""
        print(self._("app_title"))
        try:
            username = input(self._("story_username_prompt")).strip()
            if username:
                self.download_story(username)
        except KeyboardInterrupt:
            pass
        print(self._("exit_message"))


# Remove main guard and instantiate only story CLI
if __name__ == "__main__":
    stalker = InstaStalker()
    stalker.show_menu()

