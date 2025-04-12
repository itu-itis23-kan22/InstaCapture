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
        
        # Varsayılan ayarlar
        self.settings = {
            "language": "tr"
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
    
    def load_cookies(self):
        """Kaydedilmiş çerezleri yükle."""
        if self.cookies_file.exists():
            try:
                with open(self.cookies_file, 'r') as f:
                    self.cookies = json.load(f)
                cookie_keys = ', '.join(self.cookies.keys())
                print(self._("cookies_loaded", cookie_keys))
                return True
            except Exception as e:
                print(self._("cookies_not_loaded", str(e)))
        return False
    
    def save_cookies(self):
        """Çerezleri kaydet."""
        try:
            with open(self.cookies_file, 'w') as f:
                json.dump(self.cookies, f)
            os.chmod(self.cookies_file, 0o600)  # Sadece kullanıcının erişebilmesi için izinleri ayarla
            print(self._("cookies_saved", str(self.cookies_file)))
            return True
        except Exception as e:
            print(self._("cookies_not_saved", str(e)))
        return False
    
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
        try:
            # Post kodunu URL'den çıkar
            if "/" in post_url:
                # URL formatındaysa, parçala
                post_match = re.search(r'instagram\.com/(?:p|reel)/([^/?]+)', post_url)
                if post_match:
                    post_code = post_match.group(1)
                else:
                    post_code = post_url.split('/')[-1].split('?')[0]
            else:
                # Sadece kod
                post_code = post_url
            
            # Geçici klasör oluştur
            temp_dir = Path("./temp_post")
            temp_dir.mkdir(exist_ok=True)
            
            # InstaPost nesnesi oluştur
            post_obj = InstaPost()
            post_obj.reel_id = post_code
            post_obj.folder_path = str(temp_dir)
            
            # İndirme başlangıcını göster
            print(self._("downloading_post", post_code))
            start_time = time.time()
            
            # Gönderiyi indir
            result = post_obj.media_download()
            
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
                        # Geçici klasörü temizle
                        shutil.rmtree(temp_dir, ignore_errors=True)
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
                    
                    # Geçici klasörü temizle
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
                    # Sonuçları göster
                    print(self._("post_success", username, duration))
                    
                    # İndirilen medyanın detaylarını göster
                    for i, media in enumerate(media_data, 1):
                        media_type = self._("media_video") if media.get('is_video') else self._("media_image")
                        media_time = media.get('taken_at_formatted', self._("unknown_time"))
                        print(self._("story_item", i, media_type, media_time))
                    
                    print(self._("post_saved", post_dir))
                    return True
                else:
                    # Geçici klasörü temizle
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    print(self._("post_media_not_found"))
                    return False
            else:
                # Geçici klasörü temizle
                shutil.rmtree(temp_dir, ignore_errors=True)
                print(self._("post_not_found"))
                return False
                
        except Exception as e:
            # Geçici klasörü temizle
            shutil.rmtree(Path("./temp_post"), ignore_errors=True)
            print(self._("post_error", str(e)))
            return False
    
    def download_profile_picture(self, username):
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
    
    def list_downloads(self):
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
    """Ana fonksiyon - komut satırı argümanlarını işle."""
    try:
        # GUI başlatma seçeneğini ekle
        if "--gui" in sys.argv:
            # GUI modunu başlat
            try:
                from instastalk_gui import InstaStalkGUI
                app = InstaStalkGUI()
                app.mainloop()
                return
            except ImportError as e:
                print(f"GUI başlatılamadı: {e}")
                print("GUI için gerekli modüller eksik olabilir. 'pip install pillow' komutunu çalıştırın.")
                sys.exit(1)
                
        # InstaStalker nesnesi oluştur
        stalker = InstaStalker()
        
        # Komut satırı argümanlarını tanımla
        parser = argparse.ArgumentParser(description="Instagram hikayelerini ve gönderilerini indirmek için kullanıcı dostu bir araç")
        parser.add_argument("--gui", action="store_true", help="Grafik arayüzünü başlat")
        
        # Alt komutları tanımla
        subparsers = parser.add_subparsers(dest="command", help="Komut")
        
        # story komutu
        story_parser = subparsers.add_parser("story", help="Kullanıcının hikayelerini indir")
        story_parser.add_argument("username", help="Hikayeleri indirilecek kullanıcı adı")
        
        # post komutu
        post_parser = subparsers.add_parser("post", help="Gönderi veya reeli indir")
        post_parser.add_argument("url", help="Gönderi veya reel URL'si (veya kodu)")
        
        # profile komutu
        profile_parser = subparsers.add_parser("profile", help="Kullanıcının profil resmini indir")
        profile_parser.add_argument("username", help="Profil resmi indirilecek kullanıcı adı")
        
        # batch komutu
        batch_parser = subparsers.add_parser("batch", help="Toplu indirme yap")
        batch_parser.add_argument("username", help="Toplu indirme yapılacak kullanıcı adı")
        batch_parser.add_argument("--type", choices=["story", "post", "both"], default="both", 
                                help="İndirme türü (story, post, both)")
        
        # cookie komutu
        cookie_parser = subparsers.add_parser("cookie", help="Çerezleri ayarla ve kaydet")
        
        # list komutu
        list_parser = subparsers.add_parser("list", help="İndirilen dosyaları listele")
        
        # clean komutu
        clean_parser = subparsers.add_parser("clean", help="Tüm indirilen dosyaları temizle")
        
        # lang komutu
        lang_parser = subparsers.add_parser("lang", help="Dil değiştir")
        
        # args'ı parse et
        args = parser.parse_args()
        
        # Komutu yürüt
        if args.command == "story":
            stalker.download_story(args.username)
        elif args.command == "post":
            stalker.download_post(args.url)
        elif args.command == "profile":
            stalker.download_profile_picture(args.username)
        elif args.command == "batch":
            if args.type == "story":
                choice = "1"
            elif args.type == "post":
                choice = "2"
            else:
                choice = "3"
                
            # Toplu indirme başlat
            print(stalker._("batch_download_start", args.username))
            
            success = True
            
            # Hikayeleri indir
            if choice in ["1", "3"]:
                success = stalker.download_story(args.username) and success
            
            # Son gönderileri indir
            if choice in ["2", "3"]:
                success = stalker.download_recent_posts(args.username) and success
            
            if success:
                print(stalker._("batch_download_complete"))
        elif args.command == "cookie":
            stalker.get_interactive_cookies()
        elif args.command == "list":
            stalker.list_downloads()
        elif args.command == "lang":
            stalker.change_language()
        elif args.command == "clean":
            confirm = input(stalker._("clean_confirm"))
            if confirm.lower() == stalker._("yes_short"):
                shutil.rmtree(stalker.base_dir, ignore_errors=True)
                stalker.base_dir.mkdir(exist_ok=True)
                for dir_path in stalker.content_types.values():
                    dir_path.mkdir(exist_ok=True)
                print(stalker._("clean_success"))
            else:
                print(stalker._("clean_cancel"))
        elif args.gui:
            # GUI modunu başlat - bu kod yolu normalde çalışmaz, yukarıdaki kontrol işleyecektir
            try:
                from instastalk_gui import InstaStalkGUI
                app = InstaStalkGUI()
                app.mainloop()
            except ImportError as e:
                print(f"GUI başlatılamadı: {e}")
                print("GUI için gerekli modüller eksik olabilir. 'pip install pillow' komutunu çalıştırın.")
        else:
            # Eğer komut belirtilmemişse interaktif menü göster
            print(stalker._("app_name"))
            print(stalker._("menu_download_story"))
            print(stalker._("menu_download_post"))
            print(stalker._("menu_download_profile"))
            print(stalker._("menu_batch_download"))
            print(stalker._("menu_set_cookies"))
            print(stalker._("menu_list_downloads"))
            print(stalker._("menu_clean"))
            print(stalker._("menu_lang"))
            print(stalker._("menu_exit"))
            
            choice = input(stalker._("menu_choice"))
            
            if choice == "1":
                username = input(stalker._("story_username_prompt"))
                stalker.download_story(username)
            elif choice == "2":
                url = input(stalker._("post_url_prompt"))
                stalker.download_post(url)
            elif choice == "3":
                username = input(stalker._("profile_username_prompt"))
                stalker.download_profile_picture(username)
            elif choice == "4":
                username = input(stalker._("batch_username_prompt"))
                if username:
                    stalker.batch_download(username)
            elif choice == "5":
                stalker.get_interactive_cookies()
            elif choice == "6":
                stalker.list_downloads()
            elif choice == "7":
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
                stalker.change_language()
            elif choice == "9":
                print(stalker._("exit_message"))
            else:
                print(stalker._("invalid_choice"))
                
    except KeyboardInterrupt:
        print(stalker._("interrupt_message"))
        
    except Exception as e:
        print(stalker._("unexpected_error", str(e)))


if __name__ == "__main__":
    try:
        # InstaStalker nesnesi oluştur
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