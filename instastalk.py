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
        "downloading_highlight": "\n⏳ '{0}' öne çıkan hikayesi indiriliyor...",
        "highlight_success": "✅ '{0}' öne çıkan hikayesi indirildi ({1} hikaye)",
        "highlight_saved": "\nÖne çıkan hikayeler '{0}' klasörüne kaydedildi",
        "highlight_error": "❌ Öne çıkan hikayeler indirilirken bir hata oluştu: {0}",
        "highlight_cancel": "ℹ️ İşlem iptal edildi.",
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
    
    def download_post(self, post_url):
        """Belirtilen gönderiyi veya reeli indir."""
        temp_dir = Path("./temp_post")
        try:
            # Post kodunu URL'den çıkar
            if "/" in post_url:
                # URL formatındaysa, farklı desenlerle eşleştirmeyi dene
                post_match = re.search(r'instagram\.com/(?:p|reel|tv)/([^/?]+)', post_url)
                if post_match:
                    post_code = post_match.group(1)
                # Instagram kısa URL'leri için (instagram.com/p/CODE)
                elif re.search(r'instagram\.com/p/([^/?]+)', post_url):
                    post_code = re.search(r'instagram\.com/p/([^/?]+)', post_url).group(1)
                # Reel kısa URL'leri için (instagram.com/reel/CODE)
                elif re.search(r'instagram\.com/reel/([^/?]+)', post_url):
                    post_code = re.search(r'instagram\.com/reel/([^/?]+)', post_url).group(1)
                # IGTV URL'leri için (instagram.com/tv/CODE)
                elif re.search(r'instagram\.com/tv/([^/?]+)', post_url):
                    post_code = re.search(r'instagram\.com/tv/([^/?]+)', post_url).group(1)
                # Mobil URL'ler için (instagram.com/reels/CODE)
                elif re.search(r'instagram\.com/reels/([^/?]+)', post_url):
                    post_code = re.search(r'instagram\.com/reels/([^/?]+)', post_url).group(1)
                # Son çare olarak, URL'nin son parçasını kullan
                else:
                    # URL'nin son kısmını al ve query parametrelerini kaldır
                    post_code = post_url.split('/')[-1]
                    if '?' in post_code:
                        post_code = post_code.split('?')[0]
            else:
                # Sadece kod girilmişse
                post_code = post_url
            
            # Post kodunun geçerli olup olmadığını kontrol et
            if not post_code or len(post_code) < 5:
                print(self._("post_error", "Invalid post code format"))
                return False
                
            # Özel karakterleri temizle
            post_code = post_code.strip()
            
            # Geçici klasör oluştur
            temp_dir.mkdir(exist_ok=True)
            
            # InstaPost nesnesi oluştur
            post_obj = InstaPost()
            post_obj.cookies = self.cookies
            
            # InstaCapture kütüphanesi için ilgili diğer attributes
            # cookies'i farklı bir formatta (dict olarak) bekliyorsa bunu da sağlayalım
            if hasattr(post_obj, 'cookies_dict'):
                post_obj.cookies_dict = self.cookies
            
            post_obj.reel_id = post_code
            post_obj.folder_path = str(temp_dir)
            
            # İndirme başlangıcını göster
            print(self._("downloading_post", post_code))
            start_time = time.time()
            
            # Önce doğrudan URL ile deneme yapalım - Instagram API değişikliklerine karşı yedek bir çözüm
            try:
                # Doğrudan medya sayfasını getir
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.instagram.com/",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache",
                }
                
                # Daha gerçekçi tarayıcı istekleri için ek headerlar
                enhanced_headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.instagram.com/",
                    "sec-ch-ua": "\"Not A(Brand\";v=\"99\", \"Google Chrome\";v=\"121\", \"Chromium\";v=\"121\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"macOS\"",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate", 
                    "Sec-Fetch-Site": "cross-site",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "Priority": "high",
                }
                
                # Önce post sayfasını çekelim (deneme Reel URL formatı)
                post_url = f"https://www.instagram.com/p/{post_code}/"
                response = requests.get(post_url, headers=headers, cookies=self.cookies)
                
                if response.status_code == 200:
                    print("✅ Post sayfası başarıyla alındı, medya aranıyor...")
                else:
                    # Alternatif URL formatı dene (reel)
                    post_url = f"https://www.instagram.com/reel/{post_code}/"
                    response = requests.get(post_url, headers=headers, cookies=self.cookies)
                    if response.status_code == 200:
                        print("✅ Reel sayfası başarıyla alındı, medya aranıyor...")
                
                # API'den alınamayan postlar için yedek mekanizma ekle
                # Bu kod kısmı sadece instacapture kütüphanesi başarısız olursa çalışacak
            except Exception as e:
                print(f"⚠️ Post sayfası alınırken hata: {str(e)}")
            
            # Gönderiyi indir
            result = post_obj.media_download()
            
            # Hala sonuç yoksa, kendi çözümümüzü deneyelim
            if not result:
                print("⚠️ InstaCapture kütüphanesi ile post indirilemedi. Alternatif yöntem deneniyor...")
                try:
                    # Modern Instagram web uygulaması farklı veri katmanları kullanır:
                    # 1. window._sharedData (klasik format)
                    # 2. window.__additionalDataLoaded (yeni format)
                    # 3. Dahili React veri yapıları
                    # 4. Meta etiketleri

                    # 1. Klasik _sharedData formatı
                    matches = re.findall(r'window\._sharedData\s*=\s*({.*?});</script>', response.text)
                    post_data = None
                    username = None
                    
                    if matches:
                        try:
                            json_data = json.loads(matches[0])
                            # Post verilerini çıkar
                            post_data = json_data.get('entry_data', {}).get('PostPage', [{}])[0].get('graphql', {}).get('shortcode_media', {})
                            
                            if post_data:
                                # Kullanıcı adını al
                                username = post_data.get('owner', {}).get('username')
                                print(f"✅ Post verisi _sharedData formatından alındı: {username}")
                                
                                if not username:
                                    print("❌ Post sahibinin kullanıcı adı bulunamadı.")
                        except Exception as e:
                            print(f"⚠️ _sharedData ayrıştırma hatası: {str(e)}")
                    
                    # 2. Daha yeni __additionalDataLoaded formatı
                    if not post_data:
                        # Farklı varyasyonları dene - 'post' veya 'PostPage'
                        patterns = [
                            r'window\.__additionalDataLoaded\s*\(\s*[\'"]post[\'"],\s*({.*?})\);</script>',
                            r'window\.__additionalDataLoaded\s*\(\s*[\'"]PostPage[\'"],\s*({.*?})\);</script>',
                            r'window\.__additionalDataLoaded\s*\(\s*[\'"]p/[^\'\"]+[\'"],\s*({.*?})\);</script>'
                        ]
                        
                        for pattern in patterns:
                            matches2 = re.findall(pattern, response.text)
                            if matches2:
                                try:
                                    additional_data = json.loads(matches2[0])
                                    # Farklı veri yollarını dene
                                    if 'graphql' in additional_data:
                                        post_data = additional_data.get('graphql', {}).get('shortcode_media', {})
                                    elif 'items' in additional_data and len(additional_data['items']) > 0:
                                        post_data = additional_data['items'][0]
                                    
                                    if post_data:
                                        # Farklı yollardan kullanıcı adını al
                                        if 'owner' in post_data:
                                            username = post_data.get('owner', {}).get('username')
                                        elif 'user' in post_data:
                                            username = post_data.get('user', {}).get('username')
                                        
                                        print(f"✅ Post verisi additionalDataLoaded formatından alındı: {username}")
                                        break
                                except Exception as e:
                                    print(f"⚠️ additionalDataLoaded ayrıştırma hatası: {str(e)}")
                    
                    # 3. Yeni format: React yapılarındaki veri
                    if not post_data:
                        # Instagram React yapısının farklı varyasyonları
                        react_patterns = [
                            r'<script type="application/json" data-sjs>[^<]*({"require":\[.*?\]})</script>',
                            r'<script type="application/json"[^>]*>({".*?"props":.*?})</script>',
                            r'<script>window\.__bufferData\s*=\s*({.*?});</script>',
                            r'<script type="application/json" id="server-app-state">(.*?)</script>'
                        ]
                        
                        for pattern in react_patterns:
                            react_match = re.search(pattern, response.text, re.DOTALL)
                            if react_match:
                                try:
                                    react_data = json.loads(react_match.group(1))
                                    print(f"✅ React veri formatı algılandı, veri araştırılıyor...")
                                    
                                    # React yapısından medya bilgilerini çıkarmaya çalış
                                    # Mevcut yapıda kesin bir path olmadığı için JSON'ı tarayarak arıyoruz
                                    
                                    # JSON içinde kullanıcı adı arama fonksiyonu
                                    def find_username_in_json(json_obj):
                                        if isinstance(json_obj, dict):
                                            if 'username' in json_obj:
                                                return json_obj.get('username')
                                            
                                            for key, value in json_obj.items():
                                                result = find_username_in_json(value)
                                                if result:
                                                    return result
                                        elif isinstance(json_obj, list):
                                            for item in json_obj:
                                                result = find_username_in_json(item)
                                                if result:
                                                    return result
                                        return None
                                    
                                    # JSON içinde medya bilgisi arama fonksiyonu
                                    def find_media_in_json(json_obj):
                                        if isinstance(json_obj, dict):
                                            # Medya verileri içeren anahtar kontrolleri
                                            if ('shortcode_media' in json_obj or 
                                                'video_url' in json_obj or 
                                                'display_url' in json_obj or
                                                'is_video' in json_obj):
                                                return json_obj
                                            
                                            for key, value in json_obj.items():
                                                result = find_media_in_json(value)
                                                if result:
                                                    return result
                                        elif isinstance(json_obj, list):
                                            for item in json_obj:
                                                result = find_media_in_json(item)
                                                if result:
                                                    return result
                                        return None
                                    
                                    # Veri içerisinde kullanıcı adını ara
                                    username = find_username_in_json(react_data)
                                    if username:
                                        print(f"✅ React verilerinden kullanıcı adı bulundu: {username}")
                                    
                                    # Medya verilerini ara
                                    media_data = find_media_in_json(react_data)
                                    if media_data:
                                        print(f"✅ React verilerinden medya bilgileri bulundu")
                                        post_data = media_data
                                    
                                except Exception as e:
                                    print(f"⚠️ React veri ayrıştırma hatası: {str(e)}")
                    
                    # 4. Meta etiketlerinden veri çıkarma (son çare)
                    if not post_data or not username:
                        try:
                            # Kullanıcı adını meta etiketlerinden al
                            username_match = re.search(r'<meta property="og:url" content="https://www.instagram.com/([^/]+)/[^"]+"', response.text)
                            if not username_match:
                                # Alternatif pattern
                                username_match = re.search(r'instagram\.com/([^/]+)/(?:p|reel)/', response.text)
                            
                            extracted_username = None
                            if username_match:
                                extracted_username = username_match.group(1)
                                # "p" ve "reel" gibi path parçalarını username olarak kabul etme
                                if extracted_username in ["p", "reel", "tv"]:
                                    # Gerçek kullanıcı adını bulmak için farklı yöntemler dene
                                    # Instagram'ın yeni markup yapısında kullanıcı adı bulmayı dene
                                    username_alt_match = re.search(r'<meta property="og:title" content="([^"]+) on Instagram:', response.text)
                                    if username_alt_match:
                                        extracted_username = username_alt_match.group(1)
                                    else:
                                        # Farklı bir meta etiketi dene
                                        username_alt_match = re.search(r'<meta property="og:description" content="([^"]+) on Instagram:', response.text)
                                        if username_alt_match:
                                            extracted_username = username_alt_match.group(1)
                                    
                                    # Hala bulunamadıysa, genel bir ad ata
                                    if extracted_username in ["p", "reel", "tv"]:
                                        extracted_username = "instagram_user"
                                
                                username = extracted_username
                                print(f"✅ Kullanıcı adı meta etiketlerinden alındı: {username}")
                                
                                # Görsel URL'sini al
                                image_url_match = re.search(r'<meta property="og:image" content="([^"]+)"', response.text)
                                video_url_match = re.search(r'<meta property="og:video" content="([^"]+)"', response.text)
                                is_video = bool(video_url_match)
                                
                                if image_url_match or video_url_match:
                                    # Kullanıcı klasörünü ve post klasörünü oluştur
                                    user_dir = self.content_types["posts"] / username
                                    user_dir.mkdir(exist_ok=True)
                                    post_dir = user_dir / post_code
                                    post_dir.mkdir(exist_ok=True)
                                    
                                    # Geçici sonuç oluştur
                                    result = {
                                        username: {
                                            'Media Data': [{'is_video': is_video}]
                                        }
                                    }
                                    
                                    if is_video and video_url_match:
                                        # Video indir
                                        video_url = video_url_match.group(1)
                                        
                                        # 403 hatalarını ele almak için yeniden deneme mekanizması
                                        max_retries = 3
                                        retry_delay = 2  # saniye
                                        success = False
                                        
                                        for attempt in range(max_retries):
                                            # İlk denemede normal, sonraki denemelerde gelişmiş headerları kullan
                                            current_headers = headers if attempt == 0 else enhanced_headers
                                            
                                            # Referrer ve Origin headerlarını ayarla
                                            current_headers['Referer'] = f"https://www.instagram.com/p/{post_code}/"
                                            if attempt > 0:
                                                current_headers['Origin'] = "https://www.instagram.com"
                                                
                                                # URL'ye random parametre ekle (anti-caching)
                                                if '?' not in video_url:
                                                    video_url += f"?_={int(time.time())}"
                                                else:
                                                    video_url += f"&_={int(time.time())}"
                                            
                                            # Gerçek tarayıcı davranışını simüle etmek için düşük gecikme
                                            if attempt > 0:
                                                time.sleep(retry_delay)
                                                print(f"🔄 Video indirme yeniden deneniyor (deneme {attempt+1}/{max_retries})...")
                                            
                                            try:
                                                # İstek yap
                                                video_response = requests.get(video_url, stream=True, headers=current_headers, cookies=self.cookies)
                                                
                                                # Başarılı ise kaydet ve çık
                                                if video_response.status_code == 200:
                                                    # Content-Type kontrolü
                                                    content_type = video_response.headers.get('Content-Type', '')
                                                    if not content_type.startswith(('video/', 'application/')):  # MP4 bazen application/octet-stream olabilir
                                                        print(f"⚠️ İndirilen içerik bir video değil: {content_type}. Yeniden deneniyor...")
                                                        continue
                                                    
                                                    # Dosyayı kaydet
                                                    video_path = post_dir / f"{post_code}.mp4"
                                                    with open(video_path, 'wb') as f:
                                                        for chunk in video_response.iter_content(chunk_size=8192):
                                                            if chunk:
                                                                f.write(chunk)
                                                    
                                                    # Boyut kontrolü (boş dosya veya çok küçük dosya mı?)
                                                    file_size = os.path.getsize(video_path)
                                                    if file_size < 10000:  # 10KB'dan küçük
                                                        print(f"⚠️ Video dosyası çok küçük ({file_size} byte). Yeniden deneniyor...")
                                                        continue
                                                    
                                                    print(f"✅ Video meta etiketlerinden indirildi: {video_path}")
                                                    success = True
                                                    break
                                                else:
                                                    print(f"⚠️ Video indirme başarısız. HTTP kodu: {video_response.status_code}. Yeniden deneniyor...")
                                            except Exception as e:
                                                print(f"⚠️ Video indirme hatası: {str(e)}. Yeniden deneniyor...")
                                                
                                        if not success:
                                            print("❌ Video indirilemedi. Tüm denemeler başarısız oldu.")
                                            # Alternatif yöntem: web.archive.org'den dene
                                            try:
                                                print("🔄 Archive.org üzerinden video indirme deneniyor...")
                                                archive_url = f"https://web.archive.org/web/0im_/{video_url}"
                                                archive_response = requests.get(archive_url, headers=enhanced_headers, stream=True)
                                                
                                                if archive_response.status_code == 200:
                                                    video_path = post_dir / f"{post_code}.mp4"
                                                    with open(video_path, 'wb') as f:
                                                        for chunk in archive_response.iter_content(chunk_size=8192):
                                                            if chunk:
                                                                f.write(chunk)
                                                    
                                                    # Boyut kontrolü
                                                    file_size = os.path.getsize(video_path)
                                                    if file_size > 10000:
                                                        print(f"✅ Video archive.org üzerinden indirildi: {video_path}")
                                                        success = True
                                                    else:
                                                        print("❌ Archive.org üzerinden indirilen video çok küçük.")
                                                else:
                                                    print("❌ Archive.org üzerinden indirme başarısız.")
                                            except Exception as e:
                                                print(f"❌ Archive.org üzerinden indirme hatası: {str(e)}")
                                            
                                            if not success:
                                                return False
                                    
                                    elif image_url_match:
                                        # Resim indir
                                        image_url = image_url_match.group(1)
                                        
                                        # 403 hatalarını ele almak için yeniden deneme mekanizması
                                        max_retries = 3
                                        retry_delay = 2  # saniye
                                        success = False
                                        
                                        for attempt in range(max_retries):
                                            # İlk denemede normal, sonraki denemelerde gelişmiş headerları kullan
                                            current_headers = headers if attempt == 0 else enhanced_headers
                                            
                                            # Referrer ve Origin headerlarını ayarla
                                            current_headers['Referer'] = f"https://www.instagram.com/p/{post_code}/"
                                            if attempt > 0:
                                                current_headers['Origin'] = "https://www.instagram.com"
                                                
                                                # URL'ye random parametre ekle (anti-caching)
                                                if '?' not in image_url:
                                                    image_url += f"?_={int(time.time())}"
                                                else:
                                                    image_url += f"&_={int(time.time())}"
                                            
                                            # Gerçek tarayıcı davranışını simüle etmek için düşük gecikme
                                            if attempt > 0:
                                                time.sleep(retry_delay)
                                                print(f"🔄 Resim indirme yeniden deneniyor (deneme {attempt+1}/{max_retries})...")
                                            
                                            try:
                                                # İstek yap
                                                image_response = requests.get(image_url, headers=current_headers, cookies=self.cookies)
                                                
                                                # Başarılı ise kaydet ve çık
                                                if image_response.status_code == 200:
                                                    # İçerik boyutu kontrolü
                                                    content_length = len(image_response.content)
                                                    if content_length < 5000:  # 5KB'dan küçükse şüpheli
                                                        print(f"⚠️ Resim içeriği çok küçük ({content_length} byte). Yeniden deneniyor...")
                                                        continue
                                                    
                                                    # Content-Type kontrolü
                                                    content_type = image_response.headers.get('Content-Type', '')
                                                    if not content_type.startswith(('image/', 'application/')):  # Bazı JPEG'ler application/ olabilir
                                                        print(f"⚠️ İndirilen içerik bir resim değil: {content_type}. Yeniden deneniyor...")
                                                        continue
                                                    
                                                    # Dosyayı kaydet
                                                    image_path = post_dir / f"{post_code}.jpg"
                                                    with open(image_path, 'wb') as f:
                                                        f.write(image_response.content)
                                                    
                                                    print(f"✅ Resim meta etiketlerinden indirildi: {image_path}")
                                                    success = True
                                                    break
                                                else:
                                                    print(f"⚠️ Resim indirme başarısız. HTTP kodu: {image_response.status_code}. Yeniden deneniyor...")
                                            except Exception as e:
                                                print(f"⚠️ Resim indirme hatası: {str(e)}. Yeniden deneniyor...")
                                                
                                        if not success:
                                            print("❌ Resim indirilemedi. Tüm denemeler başarısız oldu.")
                                            # Alternatif yöntem: web.archive.org'den dene
                                            try:
                                                print("🔄 Archive.org üzerinden medya indirme deneniyor...")
                                                archive_url = f"https://web.archive.org/web/0im_/{image_url}"
                                                archive_response = requests.get(archive_url, headers=enhanced_headers)
                                                
                                                if archive_response.status_code == 200 and len(archive_response.content) > 5000:
                                                    image_path = post_dir / f"{post_code}.jpg"
                                                    with open(image_path, 'wb') as f:
                                                        f.write(archive_response.content)
                                                    print(f"✅ Resim archive.org üzerinden indirildi: {image_path}")
                                                    success = True
                                                else:
                                                    print("❌ Archive.org üzerinden indirme başarısız.")
                                            except Exception as e:
                                                print(f"❌ Archive.org üzerinden indirme hatası: {str(e)}")
                                            
                                            if not success:
                                                return False
                        except Exception as e:
                            print(f"⚠️ Meta etiket ayrıştırma hatası: {str(e)}")
                    
                    if not post_data and not result and not username:
                        print("❌ Post verisi hiçbir şekilde bulunamadı.")
                        print(self._("post_not_found"))
                        return False
                    
                    # Eğer post_data bulunduysa, indirme işlemini gerçekleştir
                    if post_data and username and not result:
                        # Kullanıcı klasörünü ve post klasörünü oluştur
                        user_dir = self.content_types["posts"] / username
                        user_dir.mkdir(exist_ok=True)
                        post_dir = user_dir / post_code
                        post_dir.mkdir(exist_ok=True)
                        
                        # Geçici sonuç oluştur
                        result = {
                            username: {
                                'Media Data': [{'is_video': post_data.get('is_video', False)}]
                            }
                        }
                        
                        # Medya dosyasını indir
                        if post_data.get('is_video', False):
                            # Video
                            video_url = post_data.get('video_url')
                            if not video_url:
                                # Alternatif video URL yollarını dene
                                video_versions = post_data.get('video_versions', [])
                                if video_versions and len(video_versions) > 0:
                                    video_url = video_versions[0].get('url')
                            
                            if video_url:
                                video_response = requests.get(video_url, stream=True)
                                video_path = post_dir / f"{post_code}.mp4"
                                with open(video_path, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                print(f"✅ Video dosyası indirildi: {video_path}")
                        else:
                            # Resim
                            # Farklı resim URL yollarını dene
                            image_url = None
                            
                            # 1. display_resources
                            display_resources = post_data.get('display_resources', [])
                            if display_resources:
                                # En yüksek çözünürlüklü resmi al
                                display_resources.sort(key=lambda x: x.get('config_width', 0), reverse=True)
                                image_url = display_resources[0].get('src')
                            
                            # 2. display_url
                            if not image_url:
                                image_url = post_data.get('display_url')
                            
                            # 3. image_versions2
                            if not image_url and 'image_versions2' in post_data:
                                candidates = post_data.get('image_versions2', {}).get('candidates', [])
                                if candidates and len(candidates) > 0:
                                    # En yüksek çözünürlüklü resmi al
                                    candidates.sort(key=lambda x: x.get('width', 0), reverse=True)
                                    image_url = candidates[0].get('url')
                            
                            if image_url:
                                image_response = requests.get(image_url)
                                image_path = post_dir / f"{post_code}.jpg"
                                with open(image_path, 'wb') as f:
                                    f.write(image_response.content)
                                print(f"✅ Resim dosyası indirildi: {image_path}")
                        
                        # Carousel post ise alt öğeleri indir
                        carousel_media = None
                        
                        # 1. __typename kontrolü
                        if post_data.get('__typename') == 'GraphSidecar':
                            carousel_media = post_data.get('edge_sidecar_to_children', {}).get('edges', [])
                        
                        # 2. carousel_media doğrudan kontrolü
                        elif not carousel_media and 'carousel_media' in post_data:
                            carousel_media = post_data.get('carousel_media', [])
                            carousel_media = [{'node': item} for item in carousel_media]
                        
                        # Carousel medyalarını indir
                        if carousel_media:
                            for i, edge in enumerate(carousel_media, 1):
                                node = edge.get('node', {})
                                is_video = node.get('is_video', False)
                                
                                if is_video:
                                    # Video URL'sini bul (farklı formatları dene)
                                    video_url = node.get('video_url')
                                    
                                    if not video_url:
                                        video_versions = node.get('video_versions', [])
                                        if video_versions and len(video_versions) > 0:
                                            video_url = video_versions[0].get('url')
                                    
                                    if video_url:
                                        video_response = requests.get(video_url, stream=True)
                                        video_path = post_dir / f"{post_code}_{i}.mp4"
                                        with open(video_path, 'wb') as f:
                                            for chunk in video_response.iter_content(chunk_size=8192):
                                                if chunk:
                                                    f.write(chunk)
                                        print(f"✅ Carousel video {i} indirildi: {video_path}")
                                else:
                                    # Resim URL'sini bul (farklı formatları dene)
                                    image_url = None
                                    
                                    # 1. display_resources
                                    display_resources = node.get('display_resources', [])
                                    if display_resources:
                                        display_resources.sort(key=lambda x: x.get('config_width', 0), reverse=True)
                                        image_url = display_resources[0].get('src')
                                    
                                    # 2. display_url
                                    if not image_url:
                                        image_url = node.get('display_url')
                                    
                                    # 3. image_versions2
                                    if not image_url and 'image_versions2' in node:
                                        candidates = node.get('image_versions2', {}).get('candidates', [])
                                        if candidates and len(candidates) > 0:
                                            candidates.sort(key=lambda x: x.get('width', 0), reverse=True)
                                            image_url = candidates[0].get('url')
                                    
                                    if image_url:
                                        image_response = requests.get(image_url)
                                        image_path = post_dir / f"{post_code}_{i}.jpg"
                                        with open(image_path, 'wb') as f:
                                            f.write(image_response.content)
                                        print(f"✅ Carousel resim {i} indirildi: {image_path}")
                    
                except Exception as e:
                    print(f"❌ Alternatif indirme yöntemi hatası: {str(e)}")
                    print(self._("post_not_found"))
                    return False
            
            if result:
                username = list(result.keys())[0]
                media_data = result[username].get('Media Data', [])
                duration = time.time() - start_time
                
                if media_data:
                    # Kullanıcı klasörünü oluştur
                    user_dir = self.content_types["posts"] / username
                    user_dir.mkdir(exist_ok=True)
                    
                    # Gönderi klasörünü oluştur
                    post_dir = user_dir / post_code
                    
                    # Gönderi daha önce indirilmiş mi kontrol et
                    already_downloaded = post_dir.exists()
                    
                    if already_downloaded:
                        print(f"⚠️ Bu gönderi ({post_code}) daha önce indirilmiş. Tekrar indirilmiyor.")
                        print(self._("post_saved", post_dir))
                        return True
                    
                    # Gönderi klasörünü oluştur
                    post_dir.mkdir(exist_ok=True)
                    
                    # Geçici klasörden hedef klasöre dosyaları taşı
                    temp_post_dir = temp_dir / "post" / username
                    if temp_post_dir.exists():
                        # JSON dosyalarını kopyala
                        for json_file in temp_post_dir.glob("*.json"):
                            shutil.copy(json_file, post_dir)
                        
                        # Medya dosyalarını kopyala
                        for media_file in temp_post_dir.glob("*.*"):
                            if media_file.suffix.lower() in [".mp4", ".png", ".jpg", ".jpeg"]:
                                shutil.copy(media_file, post_dir)
                    
                    # Sonuçları göster
                    print(self._("post_success", username, duration))
                    
                    # İndirilen medyanın detaylarını göster
                    for i, media in enumerate(media_data, 1):
                        media_type = self._("media_video") if media.get('is_video') else self._("media_image")
                        media_time = media.get('taken_at_formatted', self._("unknown_time"))
                        print(self._("story_item", i, media_type, media_time))
                    
                    print(self._("post_saved", post_dir))
                    return True
            
            # Eğer buraya gelindi ise, indirme başarısız olmuştur
            print(self._("post_not_found"))
            return False
                
        except Exception as e:
            print(f"❌ Post indirme hatası: {str(e)}")
            return False
        finally:
            # Her durumda geçici klasörü temizle
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass
    
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
        
        try:
            # Kullanıcı klasörünü oluştur
            user_dir = self.content_types["stories"] / username / "highlights"
            user_dir.mkdir(exist_ok=True, parents=True)
            
            # Öne çıkan hikayeleri al
            print(self._("downloading_highlights", username))
            
            # Instagram'dan kullanıcının profil sayfasını çek
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(f"https://www.instagram.com/{username}/", headers=headers, cookies=self.cookies)
            
            if response.status_code != 200:
                print(self._("no_highlights_found", username))
                return False
            
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
                print(self._("no_highlights_found", username))
                print("🔍 Instagram'ın yaptığı güncellemeler nedeniyle kullanıcı ID'si çıkarılamıyor.")
                print("💡 Kullanıcı ID'sini manuel olarak girebilirsiniz.")
                print("\nID'yi bulmak için:")
                print("1. Tarayıcıda Instagram'a gidin")
                print("2. Web Geliştirici Araçlarını açın (F12)")
                print("3. Network sekmesine tıklayın")
                print("4. Sayfayı yenileyin")
                print("5. 'graphql' içeren bir isteği bulun")
                print("6. Sorgu parametrelerinde 'user_id' değerini arayın")
                
                # Kullanıcıdan ID iste
                manual_id = input("\nKullanıcı ID'sini girin (0: İptal): ")
                
                if manual_id and manual_id.strip() and manual_id.isdigit() and manual_id != "0":
                    user_id = manual_id.strip()
                    print(f"✅ Manuel olarak girilen ID kullanılıyor: {user_id}")
                else:
                    print("❌ Geçerli bir kullanıcı ID'si girilmedi veya işlem iptal edildi.")
                    return False
                    
            # Highlights API'sine istek gönder
            # Güncel query_hash değeri kullanılıyor
            highlights_url = f"https://www.instagram.com/graphql/query/?query_hash=d4d88dc1500312af6f937f7b804c68c3&variables=%7B%22user_id%22%3A%22{user_id}%22%2C%22include_chaining%22%3Afalse%2C%22include_reel%22%3Afalse%2C%22include_suggested_users%22%3Afalse%2C%22include_logged_out_extras%22%3Afalse%2C%22include_highlight_reels%22%3Atrue%2C%22include_live_status%22%3Atrue%7D"
            
            highlights_response = requests.get(highlights_url, headers=headers, cookies=self.cookies)
            
            if highlights_response.status_code != 200:
                print(self._("no_highlights_found", username))
                return False
            
            # Highlights verilerini ayrıştır
            try:
                highlight_data = highlights_response.json()
                if not highlight_data:
                    print(f"❌ API yanıtında veri bulunamadı.")
                    return False
                
                print("ℹ️ Highlight API yanıtı inceleniyor...")
                
                # Yanıt yapısını kontrol et ve farklı formatları dene
                highlight_items = []
                
                # Otomatik olarak yanıt yapısını tespit etmeye çalış
                if 'data' in highlight_data:
                    data = highlight_data['data']
                    
                    # Olası yolları ara
                    if 'user' in data and data['user']:
                        user_data = data['user']
                        if 'edge_highlight_reels' in user_data:
                            edge_highlight_reels = user_data['edge_highlight_reels']
                            if 'edges' in edge_highlight_reels:
                                highlight_items = edge_highlight_reels['edges']
                                print("✅ Highlight verisi bulundu: data.user.edge_highlight_reels.edges yapısında")
                                
                # Hiçbir highlight bulunamadıysa JSON yapısını incele
                if not highlight_items:
                    print("ℹ️ Alternatif yapılar aranıyor...")
                    
                    # JSON yapısını yazdır (debug için)
                    debug_str = f"API yanıt yapısı (ilk 500 karakter):\n"
                    debug_str += json.dumps(highlight_data)[:500] + "...\n"
                    print(debug_str)
                    
                    # Kullanıcıya manuel giriş opsiyonu sun
                    print("\nHighlight verisini içeren JSON yolunu belirtin veya çıkmak için 0 yazın.")
                    print("Örneğin: data.user.edge_highlight_reels.edges")
                    
                    manual_path = input("> ")
                    
                    if manual_path == "0":
                        print(self._("highlight_cancel"))
                        return False
                    
                    try:
                        # Manuel yolu takip et
                        parts = manual_path.split('.')
                        current = highlight_data
                        
                        for part in parts:
                            if part.isdigit():
                                current = current[int(part)]
                            else:
                                current = current.get(part, {})
                        
                        if isinstance(current, list):
                            highlight_items = current
                            print(f"✅ Highlight verisi manuel yoldan bulundu: {manual_path}")
                        else:
                            print("❌ Belirtilen yolda liste tipi veri bulunamadı.")
                            return False
                    except Exception as e:
                        print(f"❌ Manuel yol işlenirken hata: {str(e)}")
                        return False
                
                if not highlight_items:
                    print(self._("no_highlights_found", username))
                    return False
                
                # Öne çıkan hikayeleri listele
                print(self._("highlight_selection"))
                
                highlight_info = []
                for i, highlight in enumerate(highlight_items, 1):
                    node = highlight.get('node', {})
                    title = node.get('title', f"Highlight-{i}")
                    highlight_id = node.get('id')
                    media_count = node.get('highlight_reel_count', 0)
                    
                    highlight_info.append({
                        'title': title,
                        'id': highlight_id,
                        'count': media_count
                    })
                    
                    print(self._("highlight_item", i, title, media_count))
                
                print(self._("highlight_all"))
                
                # Kullanıcıdan hangi highlight'ı indirmek istediğini sor
                choice = input(self._("highlight_choice")).strip()
                
                if choice == "0":
                    print(self._("highlight_cancel"))
                    return False
                
                # Tüm öne çıkan hikayeleri indir
                if choice.lower() == "a":
                    all_success = True
                    for highlight in highlight_info:
                        success = self._download_single_highlight(username, highlight, user_dir)
                        all_success = all_success and success
                    return all_success
                
                # Seçilen öne çıkan hikayeyi indir
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(highlight_info):
                        selected_highlight = highlight_info[choice_idx]
                        return self._download_single_highlight(username, selected_highlight, user_dir)
                    else:
                        print(self._("invalid_choice"))
                        return False
                except ValueError:
                    print(self._("invalid_choice"))
                    return False
            except Exception as e:
                print(self._("highlight_error", str(e)))
                return False
        
        except Exception as e:
            print(self._("highlight_error", str(e)))
            return False

    def _download_single_highlight(self, username, highlight, base_dir):
        """Tek bir öne çıkan hikayeyi indir."""
        title = highlight['title']
        highlight_id = highlight['id']
        
        try:
            # Highlight klasörünü oluştur
            highlight_dir = base_dir / title.replace("/", "_").replace("\\", "_")
            highlight_dir.mkdir(exist_ok=True)
            
            print(self._("downloading_highlight", title))
            
            # Highlight içeriğini al
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Güncel API query_hash ve parametrelerini kullan
            highlight_url = f"https://www.instagram.com/graphql/query/?query_hash=45246d3fe16ccc6577e0bd297a5db1ab&variables=%7B%22reel_ids%22%3A%5B%22{highlight_id}%22%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%22{highlight_id}%22%5D%2C%22precomposed_overlay%22%3Afalse%7D"
            
            highlight_response = requests.get(highlight_url, headers=headers, cookies=self.cookies)
            
            if highlight_response.status_code != 200:
                print(self._("no_highlights_found", username))
                return False
            
            # Highlight verisini ayrıştır
            try:
                highlight_data = highlight_response.json()
                if not highlight_data:
                    print(f"❌ API yanıtında veri bulunamadı.")
                    return False
                
                print("ℹ️ Highlight medya verisi inceleniyor...")
                
                # Medya içeriğine erişim için farklı JSON yapılarını dene
                media_items = []
                
                # En yaygın format: data.reels_media[0].items
                if 'data' in highlight_data and 'reels_media' in highlight_data['data']:
                    reels_media = highlight_data['data']['reels_media']
                    if reels_media and len(reels_media) > 0 and 'items' in reels_media[0]:
                        media_items = reels_media[0]['items']
                        print(f"✅ Highlight medya içeriği bulundu: {len(media_items)} öğe")
                
                # Alternatif path: data.reels.{highlight_id}.items
                if not media_items and 'data' in highlight_data and 'reels' in highlight_data['data']:
                    reels = highlight_data['data']['reels']
                    if highlight_id in reels and 'items' in reels[highlight_id]:
                        media_items = reels[highlight_id]['items']
                        print(f"✅ Highlight medya içeriği alternatif yoldan bulundu: {len(media_items)} öğe")
                
                # Hiçbir medya bulunamadıysa JSON yapısını incele ve kullanıcıdan yardım iste
                if not media_items:
                    print("❌ Medya içeriği bulunamadı. API yanıt yapısı:")
                    debug_str = json.dumps(highlight_data)[:500] + "..."
                    print(debug_str)
                    
                    print("\nMediaları içeren JSON yolunu belirtin veya çıkmak için 0 yazın.")
                    print("Örneğin: data.reels_media.0.items")
                    
                    manual_path = input("> ")
                    
                    if manual_path == "0":
                        print(self._("highlight_cancel"))
                        return False
                    
                    try:
                        # Manuel yolu takip et
                        parts = manual_path.split('.')
                        current = highlight_data
                        
                        for part in parts:
                            if part.isdigit():
                                current = current[int(part)]
                            else:
                                current = current.get(part, {})
                        
                        if isinstance(current, list):
                            media_items = current
                            print(f"✅ Medya içeriği manuel yoldan bulundu: {len(media_items)} öğe")
                        else:
                            print("❌ Belirtilen yolda liste tipi medya verisi bulunamadı.")
                            return False
                    except Exception as e:
                        print(f"❌ Manuel yol işlenirken hata: {str(e)}")
                        return False
                
                if not media_items:
                    print(f"❌ {title} için indirilebilir medya bulunamadı.")
                    return False
                
                # Highlight medyalarını indir
                downloaded_count = 0
                
                for item in media_items:
                    # Medya ID'si ve zaman damgası
                    media_id = item.get('id', 'unknown')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    is_video = item.get('is_video', False)
                    
                    if is_video:
                        # Video URL'sini bul
                        video_url = None
                        
                        # Ana video URL'si
                        if 'video_versions' in item and len(item['video_versions']) > 0:
                            video_url = item['video_versions'][0].get('url')
                        # Alternatif video kaynak yapısı
                        elif 'video_resources' in item and len(item['video_resources']) > 0:
                            video_url = item['video_resources'][0].get('src')
                        
                        if not video_url:
                            print(f"⚠️ Video URL'si bulunamadı: {media_id}")
                            continue
                        
                        # Dosya adı ve yolu
                        video_filename = f"{username}_highlight_{title}_{media_id}_{timestamp}.mp4"
                        video_path = highlight_dir / video_filename
                        
                        # Video indir
                        print(f"⏳ Video indiriliyor: {media_id}")
                        try:
                            video_response = requests.get(video_url, stream=True)
                            with open(video_path, 'wb') as f:
                                for chunk in video_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            downloaded_count += 1
                            print(f"✅ Video indirildi: {video_filename}")
                        except Exception as e:
                            print(f"❌ Video indirme hatası ({media_id}): {str(e)}")
                    else:
                        # Resim URL'sini bul
                        image_url = None
                        
                        # Ana resim URL'si
                        if 'image_versions2' in item and 'candidates' in item['image_versions2']:
                            candidates = item['image_versions2']['candidates']
                            if candidates and len(candidates) > 0:
                                image_url = candidates[0].get('url')
                        # Alternatif resim kaynak yapısı
                        elif 'display_resources' in item and len(item['display_resources']) > 0:
                            # En yüksek çözünürlüklü resmi al
                            sorted_resources = sorted(item['display_resources'], 
                                                    key=lambda x: x.get('config_width', 0), 
                                                    reverse=True)
                            image_url = sorted_resources[0].get('src')
                        
                        if not image_url:
                            print(f"⚠️ Resim URL'si bulunamadı: {media_id}")
                            continue
                        
                        # Dosya adı ve yolu
                        image_filename = f"{username}_highlight_{title}_{media_id}_{timestamp}.jpg"
                        image_path = highlight_dir / image_filename
                        
                        # Resim indir
                        print(f"⏳ Resim indiriliyor: {media_id}")
                        try:
                            image_response = requests.get(image_url)
                            with open(image_path, 'wb') as f:
                                f.write(image_response.content)
                            downloaded_count += 1
                            print(f"✅ Resim indirildi: {image_filename}")
                        except Exception as e:
                            print(f"❌ Resim indirme hatası ({media_id}): {str(e)}")
                
                print(self._("highlight_success", title, downloaded_count))
                print(self._("highlight_saved", highlight_dir))
                return downloaded_count > 0
                
            except Exception as e:
                print(f"❌ Highlight verisi ayrıştırılamadı: {str(e)}")
                return False
        
        except Exception as e:
            print(self._("highlight_error", str(e)))
            return False

        """Get posts for a specific username with a limit.
        This is a helper method for the GUI to fetch posts.
        """
        try:
            # Create InstaFeed object for getting posts
            feed_obj = InstaFeed()
            feed_obj.cookies = self.cookies
            
            # InstaCapture kütüphanesi için ilgili diğer attributes
            # cookies'i farklı bir formatta (dict olarak) bekliyorsa bunu da sağlayalım
            if hasattr(feed_obj, 'cookies_dict'):
                feed_obj.cookies_dict = self.cookies
            
            feed_obj.username = username
            feed_obj.limit = limit
            
            # Get feed data
            results = feed_obj.feed_download()
            
            if results and username in results and results[username].get('Media Data'):
                # Return the post data
                return results[username].get('Media Data', [])
            return []
        except Exception as e:
            print(f"Error in get_posts: {str(e)}")
            return []


# InstaFeed sınıfını tanımla - Kullanıcının son gönderilerini almak için
class InstaFeed:
    """Instagram kullanıcı beslemesi (feed) için basit bir sınıf."""
    
    def __init__(self):
        self.cookies = {}
        self.username = None
        self.limit = 12  # Varsayılan olarak son 12 gönderi
        self.folder_path = "./feed"
        
    def feed_download(self):
        """Kullanıcının son gönderilerini indirir ve kısa kodlarını döndürür."""
        if not self.cookies or not self.username:
            return None
            
        try:
            # Instagram kullanıcı profil URL'si
            url = f"https://www.instagram.com/{self.username}/"
            
            # Instagram'a istek gönder
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.instagram.com/",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            # Çerezleri formatlama
            cookies_dict = {k: v for k, v in self.cookies.items()}
            
            # Sayfayı getir
            response = requests.get(url, headers=headers, cookies=cookies_dict)
            
            if response.status_code != 200:
                return None
                
            # Sayfa içeriğini al
            content = response.text
            
            # JSON veri yapısını çıkarmak için regex kullan
            # shared_data değişkenini ara
            matches = re.findall(r'window\._sharedData\s*=\s*({.*?});</script>', content)
            
            if not matches:
                return None
                
            # JSON verilerini ayrıştır
            json_data = json.loads(matches[0])
            
            # Kullanıcının gönderilerini al
            user_data = json_data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {})
            
            if not user_data:
                # Alternatif yöntem: additional_data'dan al
                matches2 = re.findall(r'window\.__additionalDataLoaded\s*\(\s*[\'"]feed[\'"],\s*({.*?})\);</script>', content)
                if matches2:
                    additional_data = json.loads(matches2[0])
                    user_data = additional_data.get('graphql', {}).get('user', {})
            
            if not user_data:
                return None
                
            # Timeline gönderilerini al
            edge_owner_to_timeline_media = user_data.get('edge_owner_to_timeline_media', {})
            edges = edge_owner_to_timeline_media.get('edges', [])
            
            # Gönderi kısa kodlarını topla
            post_codes = []
            for edge in edges[:self.limit]:  # Sadece belirtilen sayıda gönderi al
                node = edge.get('node', {})
                shortcode = node.get('shortcode')
                if shortcode:
                    post_codes.append(shortcode)
            
            # Sonuçları döndür
            result = {
                self.username: {
                    'Media Data': post_codes
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Hata: {str(e)}")
            return None


def main():
    try:
        stalker = InstaStalker()
        
        while True:
            print("\n" + "="*50)
            print(stalker._("app_title"))
            print("="*50)
            
            print("\n" + stalker._("app_name"))
            print("1. " + stalker._("menu_download_story"))
            print("2. " + stalker._("menu_download_post"))
            print("3. " + stalker._("menu_download_profile"))
            print("4. " + stalker._("menu_set_cookies"))
            print("5. " + stalker._("menu_list_downloads"))
            print("6. " + stalker._("menu_batch_download"))
            print("7. " + stalker._("menu_clean"))
            print("8. " + stalker._("menu_lang"))
            print("9. " + stalker._("menu_9"))
            print("10. " + stalker._("menu_10"))
            print("0. " + stalker._("menu_exit"))
            
            choice = input(stalker._("menu_choice"))
            
            if choice == "1":
                # Hikaye indirme
                username = input(stalker._("username_prompt"))
                stalker.download_story(username)
            
            elif choice == "2":
                # Gönderi indirme
                post_url = input(stalker._("post_url_prompt"))
                stalker.download_post(post_url)
            
            elif choice == "3":
                # Profil resmi indirme
                username = input(stalker._("username_prompt"))
                stalker.download_profile_pic(username)
            
            elif choice == "4":
                # Çerezleri ayarla
                stalker.get_interactive_cookies()
            
            elif choice == "5":
                # İndirilen dosyaları listele
                stalker.list_downloaded_files()
            
            elif choice == "6":
                # Toplu indirme
                batch_username = input(stalker._("batch_username_prompt"))
                stalker.batch_download(batch_username)
            
            elif choice == "7":
                # İndirilen dosyaları temizle
                confirm = input(stalker._("clean_confirm"))
                if confirm.lower() == stalker._("yes_short"):
                    shutil.rmtree(stalker.base_dir, ignore_errors=True)
                    stalker.base_dir.mkdir(exist_ok=True)
                    for dir_path in stalker.content_types.values():
                        dir_path.mkdir(exist_ok=True)
                    print(stalker._("clean_success"))
                else:
                    print(stalker._("clean_cancel"))
            
            elif choice == "8":
                # Dil değiştir
                stalker.change_language()
                
            elif choice == "9":
                # Şifreleme aç/kapat
                stalker.toggle_encryption()
                
            elif choice == "10":
                # Öne çıkan hikayeleri indir
                username = input(stalker._("highlight_username_prompt"))
                stalker.download_highlights(username)
            
            elif choice == "0":
                # Çıkış
                print(stalker._("exit_message"))
                break
                
            else:
                print(stalker._("invalid_choice"))
                
    except KeyboardInterrupt:
        print(stalker._("interrupt_message"))
        
    except Exception as e:
        print(stalker._("unexpected_error", str(e)))


if __name__ == "__main__":
    try:
        stalker = InstaStalker()
        print(stalker._("app_title"))
        main()
    except KeyboardInterrupt:
        # InstaStalker nesnesi oluştur
        stalker = InstaStalker()
        print(stalker._("interrupt_message"))
    except Exception as e:
        # InstaStalker nesnesi oluştur
        stalker = InstaStalker()
        print(stalker._("unexpected_error", str(e))) 