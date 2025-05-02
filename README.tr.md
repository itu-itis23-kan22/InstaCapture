# InstaCapture

**InstaCapture, yalnızca Instagram hikayelerini indirmek için kullanılan basit bir komut satırı aracıdır.**

[README in English](README.md)

## Genel Bakış

InstaCapture, Instagram hikayelerini arşivlemek veya çevrimdışı görüntülemek için kullanılan basit bir komut satırı aracıdır ve sadece hikaye indirmeye odaklanır (geçerli Instagram çerezleri gerektirir).

## Özellikler

- 📸 **Hikaye İndirme**: Takip ettiğiniz kullanıcıların hikayelerini indirin
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

1. Uygulamayı çalıştırın:
   ```bash
   python instastalk.py
   ```
2. Seçeneklerden birini seçin:
   - 1. **Story Stalk**: Hikayelerini indirmek için kullanıcı adı girin.
   - 2. **Çerezleri Değiştir**: Yeni Instagram çerezlerini yapıştırın.
   - 3. **Dil Değiştir**: Türkçe ve İngilizce arasında geçiş yapın.
   - 0. **Çıkış**: Uygulamadan çıkın.

### İndirme Konumu

Tüm indirilen hikayeler `instagram_content/stories/<kullanıcı adı>/` klasörüne kaydedilir.

## Sorun Giderme

- **Çerez Gereklidir**: Özel hesap içeriklerine erişmek için geçerli Instagram çerezlerinizi ayarlayın
- **İçerik Bulunamadı**: Doğru kullanıcı adı kullandığınızdan ve geçerli çerezlere sahip olduğunuzdan emin olun
- **Çerezler Süresi Doldu**: Seçenek 2 (Çerezleri Değiştir) ile çerezleri tekrar ayarlayın

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.