# 📱 InstaCapture (InstaStalker)

Instagram içeriklerini indirmek için kullanıcı dostu bir araç.

> ⚠️ **Önemli Not**: Bu proje eğitim amaçlı geliştirilmiştir ve sadece kişisel kullanım için tasarlanmıştır. Instagram'ın kullanım şartlarına uygun şekilde kullanılması kullanıcının sorumluluğundadır.

## 🌟 Özellikler

- 📸 **Hikayeleri İndirme**: Kullanıcı adı ile hikayeleri indirebilirsiniz
- 🎬 **Gönderi/Reel İndirme**: Instagram gönderilerini veya reellerini URL ile indirebilirsiniz
- 👤 **Profil Resmi İndirme**: Kullanıcı adı ile profil resimlerini indirebilirsiniz
- 🔄 **Toplu İndirme**: Bir kullanıcının tüm içeriklerini tek seferde indirebilirsiniz
- 🌐 **Çoklu Dil Desteği**: Türkçe ve İngilizce dil seçenekleri
- 🖥️ **Komut Satırı ve GUI Arayüzü**: İhtiyacınıza göre iki farklı kullanım seçeneği

## 📋 Gereksinimler

- Python 3.6 veya üzeri
- Aşağıdaki Python kütüphaneleri:
  - instacapture
  - requests
  - pillow (GUI için)
  - tkinter (GUI için)

## 🚀 Kurulum ve Başlatma

### Paketleri Yükleme
```bash
# Gerekli kütüphaneleri yükleyin
pip install instacapture requests pillow
```

### Windows Kullanıcıları İçin
1. İndirdiğiniz dosyalarda `InstaCapture.pyw` veya `StartInstaCapture.bat` dosyasına çift tıklayın.
2. Alternatif olarak komut satırında:
```bash
python instastalk.py        # Komut satırı arayüzü için
python instastalk_gui.py    # Grafik arayüzü için
```

### macOS Kullanıcıları İçin
1. İndirdiğiniz dosyalarda `InstaCapture.command` dosyasına çift tıklayın.
2. Alternatif olarak Terminal'de:
```bash
python3 instastalk.py       # Komut satırı arayüzü için 
python3 instastalk_gui.py   # Grafik arayüzü için
```

### Linux Kullanıcıları İçin
Terminal'de:
```bash
python3 instastalk.py       # Komut satırı arayüzü için
python3 instastalk_gui.py   # Grafik arayüzü için
```

### Kolay Erişim İçin Kısayol Oluşturma
Masaüstüne kısayol oluşturmak için:
```bash
python desktop_shortcut_setup.py
```

## 🔧 Kullanım

### Hikaye İndirme

Hikayeleri indirmek için Instagram çerezlerinizi ayarlamanız gerekiyor:

1. Chrome/Safari'de Instagram.com adresine gidin ve giriş yapın
2. Tarayıcıda herhangi bir yere sağ tıklayın ve 'İncele' seçeneğini seçin
3. Açılan geliştirici araçlarında 'Ağ' sekmesine tıklayın
4. Sayfayı yenileyin (F5)
5. 'instagram.com' ile başlayan bir isteği seçin
6. 'Başlıklar' sekmesinde 'Request Headers' kısmında 'Cookie:' satırını bulun
7. Cookie satırını tam olarak kopyalayın

### İndirilen İçeriklerin Konumu

İndirilen tüm dosyalar `instagram_content` klasörü içinde saklanır:

- `instagram_content/stories/` - İndirilen hikayeler
- `instagram_content/posts/` - İndirilen gönderiler ve reeller
- `instagram_content/profiles/` - İndirilen profil resimleri

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🔒 Güvenlik

- Çerezleriniz sadece kendi bilgisayarınızda, `~/.instastalk/cookies.json` dosyasında saklanır.
- Çerezler veya hesap bilgileriniz hiçbir sunucuya gönderilmez.
- Uygulama, çerezleri yalnızca Instagram API isteklerini yetkilendirmek için kullanır.

## 📝 Eğitim Amaçlı Proje

Bu proje, Python programlama becerilerini geliştirmek, API kullanımını öğrenmek ve kullanıcı arayüzü tasarımı konularında deneyim kazanmak için eğitim amaçlı geliştirilmiştir. Aşağıdaki eğitim konularını içerir:

- HTTP istekleri ve çerez yönetimi
- API entegrasyonu
- Çoklu dil desteği
- Komut satırı ve grafik kullanıcı arayüzü (GUI) geliştirme
- Dosya sistemi işlemleri
- Python modül mimarisi
