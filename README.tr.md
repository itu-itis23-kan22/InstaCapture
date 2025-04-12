# 📱 InstaCapture (InstaStalker)

Instagram hikayeleri, gönderileri, reelleri ve profil resimleri dahil olmak üzere içerikleri indirmek için kullanıcı dostu bir araç.

![InstaCapture Logo](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/logo.png)

> ⚠️ **Önemli Not**: Bu proje eğitim amaçlı geliştirilmiştir ve sadece kişisel kullanım için tasarlanmıştır. Instagram'ın kullanım şartlarına uygun şekilde kullanılması kullanıcının sorumluluğundadır. Bu projenin geliştiricileri, Instagram'ın kullanım koşullarının yanlış kullanımından veya ihlalinden sorumlu değildir.

## 📖 Genel Bakış

InstaCapture, kullanıcıların çeşitli Instagram içeriklerini çevrimdışı görüntüleme için indirmelerine olanak tanıyan Python tabanlı bir uygulamadır. Proje, modern Python uygulama geliştirme tekniklerini, API entegrasyonunu ve kullanıcı arayüzü tasarımını gösterir.

İster komut satırı arayüzünü ister grafiksel kullanıcı arayüzünü tercih edin, InstaCapture ihtiyaçlarınıza uygun her iki seçeneği de sunar.

## 🌟 Özellikler

- 📸 **Hikayeleri İndirme**: Kullanıcı adı ile hikayeleri indirebilirsiniz
  - Geçici hikayeleri kaybolmadan önce görüntüleyin ve kaydedin
  - Hikayelerden hem resim hem de video kaydedin
  - Zaman damgaları dahil hikaye meta verilerini koruyun

- 🎬 **Gönderi/Reel İndirme**: Instagram gönderilerini veya reellerini URL ile indirebilirsiniz
  - Çoklu resim/video içeren gönderilerden tüm medyayı çıkarın
  - Reelleri orijinal kalitede indirin
  - Gönderi açıklamalarını ve meta verilerini kaydedin

- 👤 **Profil Resmi İndirme**: Kullanıcı adı ile profil resimlerini indirebilirsiniz
  - Tam çözünürlüklü profil resimleri alın
  - Hem açık hem de gizli hesaplar için çalışır (çerezler sağlanırsa)

- 🔄 **Toplu İndirme**: Bir kullanıcının tüm içeriklerini tek seferde indirebilirsiniz
  - Hikayeler ve son gönderileri birlikte indirme
  - Paralel indirmelerle verimli işleme
  - Kolay gezinme için düzenli dosya yapısı

- 🌐 **Çoklu Dil Desteği**: Türkçe ve İngilizce dil seçenekleri
  - Tam arayüz çevirisi
  - Menüden kolayca diller arası geçiş
  - Dil ayarları oturumlar arasında kaydedilir

- 🖥️ **Komut Satırı ve GUI Arayüzü**: İhtiyacınıza göre iki farklı kullanım seçeneği
  - Komut dosyası oluşturma ve otomasyon için güçlü komut satırı arayüzü
  - Sezgisel kontroller ve görsel geri bildirim ile kullanıcı dostu GUI
  - Her iki arayüzde de tutarlı işlevsellik

## 🔍 Ekran Görüntüleri

![CLI Arayüzü](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/cli_screenshot.png)
*Hikaye indirmeyi gösteren komut satırı arayüzü*

![GUI Arayüzü](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/gui_screenshot.png)
*İndirme seçenekleri ile grafiksel kullanıcı arayüzü*

## 📋 Gereksinimler

- Python 3.6 veya üzeri
- Aşağıdaki Python kütüphaneleri:
  - instacapture: Instagram içeriği indirme için temel işlevsellik
  - requests: Instagram sunucularına HTTP istekleri için
  - pillow: GUI için görüntü işleme (sadece CLI kullanıyorsanız isteğe bağlı)
  - tkinter: GUI çerçevesi (çoğu Python kurulumu ile birlikte gelir, sadece CLI kullanıyorsanız isteğe bağlı)

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
   - İzin hatası alırsanız, önce Terminal'de `chmod +x InstaCapture.command` komutunu çalıştırın
   - "macOS, 'InstaCapture.command' öğesinin Mac'inize zarar verebilecek veya gizliliğinizi ihlal edebilecek bir kötü amaçlı yazılım içermediğini doğrulayamadı" şeklinde bir güvenlik uyarısı görürseniz:
     1. Sistem Tercihleri > Güvenlik ve Gizlilik'i açın
     2. Değişiklik yapmak için kilit simgesine tıklayın (şifrenizi girin)
     3. "'InstaCapture.command' engellendi" mesajını bulun ve "Yine de Aç" düğmesine tıklayın
     4. Dosyaya geri dönün ve tekrar çift tıklayın, sorulduğunda "Aç" düğmesine tıklayın
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
Bu, işletim sisteminize göre masaüstünüzde bir kısayol oluşturarak uygulamaya kolay erişim sağlar.

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
8. Sorulduğunda InstaCapture'a yapıştırın

![Çerez Talimatları](https://raw.githubusercontent.com/itu-itis23-kan22/InstaCapture/main/assets/cookie_instructions.png)
*Çerez değerini bulma yöntemi*

### Gönderi/Reel İndirme

1. Instagram'da indirmek istediğiniz gönderiyi veya reeli bulun
2. Tarayıcı adres çubuğundan URL'yi kopyalayın
3. URL'yi InstaCapture'a yapıştırın
4. Gönderi ve tüm medyası otomatik olarak indirilecektir

### Toplu İndirme

1. Toplu olarak indirmek istediğiniz kullanıcı adını girin
2. Hikayeler, Gönderiler veya her ikisini de indirmeyi seçin
3. İndirmenin tamamlanmasını bekleyin
4. Tüm içerikler ayrı klasörlerde düzenlenecektir

### İndirilen İçeriklerin Konumu

İndirilen tüm dosyalar `instagram_content` klasörü içinde saklanır:

- `instagram_content/stories/` - İndirilen hikayeler
  - Kullanıcı adına göre düzenlenmiş
  - Her hikaye zaman damgası bilgisine sahiptir
- `instagram_content/posts/` - İndirilen gönderiler ve reeller
  - Kullanıcı adı ve gönderi kimliğine göre düzenlenmiş
  - JSON meta veri dosyaları içerir
- `instagram_content/profiles/` - İndirilen profil resimleri
  - Kullanıcı adına göre düzenlenmiş

## ⚠️ Sorun Giderme

### Yaygın Sorunlar

1. **"Çerez Hatası" veya "Hikayeler indirilemiyor"**
   - Instagram'dan tüm çerez dizesini kopyaladığınızdan emin olun
   - Instagram oturumunuzun hala aktif olduğunu kontrol edin
   - Çerezleriniz süresi dolmuş olabilir; Instagram'dan çıkış yapın ve tekrar giriş yapın

2. **"Modül bulunamadı" hataları**
   - Tüm bağımlılıkları yüklemek için `pip install -r requirements.txt` komutunu çalıştırın
   - Python 3.6 veya daha yüksek bir sürüm kullandığınızdan emin olun

3. **GUI görünmüyor**
   - Tkinter'ın kurulu olduğundan emin olun (çoğu Python kurulumu ile birlikte gelir)
   - Hata mesajlarını görmek için komut satırından çalıştırmayı deneyin
   - Eğer "Lütfen Python'u Tkinter desteğiyle yeniden kurun" gibi bir hata mesajı görürseniz, aşağıdaki talimatları izleyin:
     - **macOS**: `brew install python-tk` veya `brew reinstall python` komutunu çalıştırın
     - **Linux (Debian/Ubuntu)**: `sudo apt-get update && sudo apt-get install python3-tk` komutunu çalıştırın
     - **Linux (Fedora)**: `sudo dnf install python3-tkinter` komutunu çalıştırın
     - **Windows**: Python'u Tkinter seçenekleri işaretlenmiş olarak yeniden yükleyin. Kurulum sırasında "Özel kurulum" seçeneğini seçin ve "tcl/tk ve IDLE" seçeneğinin işaretli olduğundan emin olun
   - Tkinter'ın düzgün kurulup kurulmadığını test etmek için şu komutu çalıştırın: `python -c "import tkinter; tkinter._test()"`

4. **macOS/Linux'ta izin hataları**
   - macOS için `chmod +x InstaCapture.command` komutunu çalıştırın
   - Hedef klasör için yazma izinleriniz olduğundan emin olun
   - macOS'ta "macOS, 'InstaCapture.command' öğesinin Mac'inize zarar verebilecek veya gizliliğinizi ihlal edebilecek bir kötü amaçlı yazılım içermediğini doğrulayamadı" mesajını görürseniz, uygulamanın çalışmasına izin vermek için Kurulum bölümündeki adımları takip edin (Güvenlik ve Gizlilik ayarlarını kullanarak)

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🔒 Güvenlik

- Çerezleriniz sadece kendi bilgisayarınızda, `~/.instastalk/cookies.json` dosyasında saklanır.
- Çerezler veya hesap bilgileriniz hiçbir sunucuya gönderilmez.
- Uygulama, çerezleri yalnızca Instagram API isteklerini yetkilendirmek için kullanır.
- Güvenlik konusunda endişeleriniz varsa, test için özel bir Instagram hesabı kullanmanızı öneririz.

## 📝 Eğitim Amaçlı Proje

Bu proje, Python programlama becerilerini geliştirmek, API kullanımını öğrenmek ve kullanıcı arayüzü tasarımı konularında deneyim kazanmak için eğitim amaçlı geliştirilmiştir. Aşağıdaki eğitim konularını içerir:

- HTTP istekleri ve çerez yönetimi
- API entegrasyonu ve veri ayrıştırma
- Çoklu dil desteği ve uluslararasılaştırma
- Komut satırı ve grafik kullanıcı arayüzü (GUI) geliştirme
- Dosya sistemi işlemleri ve veri organizasyonu
- Python modül mimarisi ve proje yapılandırma
- Hata işleme ve kullanıcı geri bildirimi

## 🤝 Katkıda Bulunma

InstaCapture'a katkıda bulunmak isteyenler memnuniyetle karşılanır! Katkıda bulunmak isterseniz, lütfen:

1. Depoyu fork edin
2. Bir özellik dalı oluşturun (`git checkout -b feature/harika-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Harika bir özellik ekle'`)
4. Dalınıza iteleyebilirsiniz (`git push origin feature/harika-ozellik`)
5. Bir Pull Request açın

Daha fazla ayrıntı için [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın.

## ❓ Sıkça Sorulan Sorular

**S: Bu aracı kullanmak yasal mı?**
C: Aracın kendisi yasaldır, ancak nasıl kullandığınız önemlidir. Yalnızca erişim izniniz olan içeriği indirin ve telif hakkı yasalarına ve Instagram'ın hizmet şartlarına saygı gösterin.

**S: Bunu kullanmak için bir Instagram hesabına ihtiyacım var mı?**
C: Evet, çoğu içeriği, özellikle hikayeleri indirmek için bir Instagram hesabına ve geçerli çerezlere ihtiyacınız vardır.

**S: Çerezlerimi ne sıklıkla güncellemem gerekiyor?**
C: Instagram oturumları genellikle 1-2 hafta sürer. Oturumunuzun süresi dolduğunda çerezlerinizi güncellemeniz gerekecektir.

**S: Özel hesaplardan içerik indirebilir miyim?**
C: Yalnızca çerezlerini kullandığınız hesapla takip ettiğiniz özel hesaplardan içerik indirebilirsiniz.

**S: Araç aniden neden çalışmıyor?**
C: Instagram sık sık API'sini ve web arayüzünü günceller. Araç çalışmayı durdurursa, InstaCapture projesinin güncellemelerini kontrol edin. 