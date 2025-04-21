# InstaCapture

**InstaCapture, hikayeler, gönderiler, reels ve profil resimlerini indirmek için kullanılan bir komut satırı aracıdır.**

[README in English](README.md)

## Genel Bakış

InstaCapture, Instagram içeriklerini arşivlemek veya çevrimdışı görüntülemek için indirme olanağı sağlar. Hikayeler, gönderiler ve profil resimlerini indirmek için kullanımı kolay bir komut satırı arayüzü sunar.

## Özellikler

- 📸 **Hikaye İndirme**: Takip ettiğiniz herhangi bir kullanıcının hikayelerini kaydedin
- 🖼️ **Gönderi İndirme**: Fotoğraf ve videoları indirin
- 📹 **Reels Desteği**: Instagram reels videolarını indirin
- 👤 **Profil Resimleri**: Tam çözünürlüklü profil resimlerini indirin
- 🔄 **Toplu İndirme**: Birden fazla hikaye veya gönderiyi tek seferde indirin
- 🔒 **Özel Hesap Desteği**: Takip ettiğiniz özel hesaplardan içerik erişimi
- 🌍 **Çok Dilli**: Türkçe ve İngilizce seçenekleri
- 🖥️ **Komut Satırı Arayüzü**: Terminalden kolay kullanım

## Gereksinimler

- Python 3.7 veya üzeri
- Gerekli paketler:
  - instacapture
  - pytz
  - requests
  - lxml
  - cryptography
  - brotli

## Kurulum & Kullanım

### Windows
```bash
# Depoyu klonlayın
git clone https://github.com/itu-itis23-kan22/InstaCapture.git
cd InstaCapture

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
python instastalk.py
```

### macOS / Linux
```bash
# Depoyu klonlayın
git clone https://github.com/itu-itis23-kan22/InstaCapture.git
cd InstaCapture

# Gerekli paketleri yükleyin
pip3 install -r requirements.txt

# Uygulamayı çalıştırın
python3 instastalk.py
```

## Kullanım

### Hikaye İndirme
1. Uygulamayı çalıştırın: `python instastalk.py`
2. Seçenek menüsünden **Hikaye İndir**'i seçin
3. Hikayeleri indirmek istediğiniz kullanıcı adını girin
4. Hikayeler, `instagram_content/stories/` klasörüne kaydedilecektir

### Gönderi/ Reels İndirme
1. Uygulamayı çalıştırın: `python instastalk.py`
2. **Gönderi/Reel İndir** seçeneğini seçin
3. Instagram gönderi URL'sini girin (örn. https://www.instagram.com/p/ABC123/)
4. İçerik, `instagram_content/posts/` klasörüne kaydedilecektir

## Sorun Giderme

- **Çerez Gereklidir**: Özel hesap içeriklerine erişmek için geçerli Instagram çerezlerinizi ayarlayın
- **İçerik Bulunamadı**: Doğru kullanıcı adı veya URL kullandığınızdan emin olun
- **Çerezler Süresi Doldu**: Option 5 ile çerezleri tekrar ayarlayın

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.