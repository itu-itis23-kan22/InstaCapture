# InstaCapture

**InstaCapture, yalnızca Instagram hikayelerini indirmek için kullanılan basit bir komut satırı aracıdır.**

[README in English](README.md)

## Genel Bakış

InstaCapture, Instagram hikayelerini arşivlemek veya çevrimdışı görüntülemek için kullanılan basit bir komut satırı aracıdır. Hikayeler, gönderiler ve profil resimlerini indirmek için kullanımı kolay bir komut satırı arayüzü sunar.

## Özellikler

- 📸 **Hikaye İndirme**: Takip ettiğiniz kullanıcıların hikayelerini indirin
- 🖼️ **Gönderi İndirme**: Fotoğraf ve videoları indirin
- �� **Reels Desteği**: Instagram reels videolarını indirin
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
2. Hikayeleri indirmek istediğiniz kullanıcı adını girin
3. Hikayeler, `instagram_content/stories/` klasörüne kaydedilecektir

## Sorun Giderme

- **Çerez Gereklidir**: Özel hesap içeriklerine erişmek için geçerli Instagram çerezlerinizi ayarlayın
- **İçerik Bulunamadı**: Doğru kullanıcı adı veya URL kullandığınızdan emin olun
- **Çerezler Süresi Doldu**: Option 5 ile çerezleri tekrar ayarlayın

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.