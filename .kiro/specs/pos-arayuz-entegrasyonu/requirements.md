# POS Arayüz Entegrasyonu - Gereksinimler Belgesi

## Giriş

Bu belge, SONTECHSP sisteminde POS (Point of Sale) arayüzünün tam entegrasyonu ve gerçek POS ekranının tasarlanması için gereksinimleri tanımlar. Mevcut sistem temel altyapıya sahip ancak POS ekranları henüz AnaPencere'ye entegre edilmemiş ve gerçek POS arayüzü eksiktir.

## Sözlük

- **AnaPencere**: Ana uygulama penceresi, tüm modül ekranlarını barındıran container
- **POS_Sistemi**: Point of Sale - Satış noktası sistemi
- **Sepet**: Müşteri alışveriş sepeti, satış öncesi ürün listesi
- **Barkod**: Ürün tanımlama kodu
- **Terminal**: POS cihazı/istasyonu
- **Kasiyer**: Satış işlemini gerçekleştiren kullanıcı
- **Fiş**: Satış makbuzu
- **Fatura**: Resmi satış belgesi
- **QStackedWidget**: PyQt6 widget'ı, birden fazla ekranı üst üste yerleştiren container
- **Handler**: UI olaylarını işleyen fonksiyon
- **Servis_Katmani**: İş kurallarını içeren servis katmanı
- **Stub**: Geçici/test amaçlı kod parçası
- **Hızlı_Ürün_Butonu**: Sık satılan ürünler için önceden tanımlanmış buton
- **Bekletme_İşlemi**: Mevcut sepeti geçici olarak saklama işlemi
- **Ödeme_Türü**: Nakit, kart, parçalı veya açık hesap ödeme seçenekleri
- **Eşleştirme_Tablosu**: Buton-handler-servis ilişkilerini gösteren tablo

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Bir kasiyer olarak, uygulamayı açtığımda tüm POS ekranlarına sol menüden erişebilmek istiyorum, böylece satış işlemlerimi kesintisiz gerçekleştirebilirim.

#### Kabul Kriterleri

1. WHEN uygulama başlatıldığında THEN AnaPencere sol menüsünde "POS Satış" seçeneği görünür olacaktır
2. WHEN "POS Satış" menü öğesi tıklandığında THEN POS_Sistemi gerçek satış ekranını açacaktır
3. WHEN POS ekranı açıldığında THEN POS_Sistemi tam fonksiyonel bileşenleri gösterecektir
4. WHEN menü öğeleri arasında geçiş yapıldığında THEN POS_Sistemi ekran durumunu koruyacaktır
5. WHEN uygulama yeniden başlatıldığında THEN AnaPencere varsayılan dashboard ekranını gösterecektir

### Gereksinim 2

**Kullanıcı Hikayesi:** Bir kasiyer olarak, POS ekranında barkod okuyup ürün ekleyebilmek istiyorum, böylece hızlı satış işlemi yapabilirim.

#### Kabul Kriterleri

1. WHEN POS ekranı açıldığında THEN POS_Sistemi üst kısımda barkod arama alanını gösterecektir
2. WHEN barkod alanına kod girilip Enter tuşuna basıldığında THEN POS_Sistemi ürünü Sepet'e ekleyecektir
3. WHEN geçersiz barkod girildiğinde THEN POS_Sistemi hata mesajını gösterecektir
4. WHEN EKLE butonuna tıklandığında THEN POS_Sistemi barkod alanındaki kodu işleyecektir
5. WHEN F2 tuşuna basıldığında THEN POS_Sistemi barkod alanına odak verecektir

### Gereksinim 3

**Kullanıcı Hikayesi:** Bir kasiyer olarak, sepetteki ürünleri görebilmek ve yönetebilmek istiyorum, böylece satış öncesi kontrol yapabilirim.

#### Kabul Kriterleri

1. WHEN ürün Sepet'e eklendiğinde THEN POS_Sistemi ürünü sepet tablosunda gösterecektir
2. WHEN sepet tablosu görüntülendiğinde THEN POS_Sistemi Barkod, Ürün, Adet, Fiyat, Tutar, Sil kolonlarını gösterecektir
3. WHEN sepet satırı seçildiğinde THEN POS_Sistemi adet artırma ve azaltma kısayollarını aktif edecektir
4. WHEN sepet satırındaki sil butonuna tıklandığında THEN POS_Sistemi satırı Sepet'ten kaldıracaktır
5. WHEN Sepet boş olduğunda THEN POS_Sistemi "Sepet boş" mesajını gösterecektir

### Gereksinim 4

**Kullanıcı Hikayesi:** Bir kasiyer olarak, farklı ödeme türleriyle ödeme alabilmek istiyorum, böylece müşteri tercihlerine göre işlem yapabilirim.

#### Kabul Kriterleri

1. WHEN ödeme paneli görüntülendiğinde THEN POS_Sistemi AraToplam, İndirim, GenelToplam göstergelerini gösterecektir
2. WHEN ödeme türü butonları görüntülendiğinde THEN POS_Sistemi NAKİT, KART, PARÇALI, AÇIK HESAP seçeneklerini gösterecektir
3. WHEN nakit Ödeme_Türü seçildiğinde THEN POS_Sistemi alınan para alanı ve para üstü hesaplamasını gösterecektir
4. WHEN parçalı Ödeme_Türü seçildiğinde THEN POS_Sistemi nakit ve kart tutar girişi için dialog açacaktır
5. WHEN açık hesap Ödeme_Türü seçildiğinde ve müşteri seçili değilse THEN POS_Sistemi uyarı mesajı gösterecektir

### Gereksinim 5

**Kullanıcı Hikayesi:** Bir kasiyer olarak, hızlı ürün butonlarını kullanabilmek istiyorum, böylece sık satılan ürünleri hızla ekleyebilirim.

#### Kabul Kriterleri

1. WHEN hızlı ürün paneli görüntülendiğinde THEN POS_Sistemi 12 ile 24 arasında Hızlı_Ürün_Butonu gösterecektir
2. WHEN kategori seçimi yapıldığında THEN POS_Sistemi seçilen kategorinin ürün butonlarını gösterecektir
3. WHEN Hızlı_Ürün_Butonu tıklandığında THEN POS_Sistemi ürünü Sepet'e ekleyecektir
4. WHEN Hızlı_Ürün_Butonu boş olduğunda THEN POS_Sistemi "Tanımsız" etiketini gösterecektir
5. WHEN hızlı ürün kategorisi değiştirildiğinde THEN POS_Sistemi butonları güncelleyecek ve yeni kategori ürünlerini gösterecektir

### Gereksinim 6

**Kullanıcı Hikayesi:** Bir kasiyer olarak, POS işlem kısayollarını kullanabilmek istiyorum, böylece hızlı ve verimli çalışabilirim.

#### Kabul Kriterleri

1. WHEN işlem kısayolları paneli görüntülendiğinde THEN POS_Sistemi BEKLET, BEKLEYENLER, İADE, İPTAL, FİŞ YAZDIR, FATURA butonlarını gösterecektir
2. WHEN BEKLET butonuna tıklandığında THEN POS_Sistemi mevcut Sepet'i bekletecek ve yeni Sepet başlatacaktır
3. WHEN BEKLEYENLER butonuna tıklandığında THEN POS_Sistemi bekletilen sepetler listesini gösterecektir
4. WHEN İADE butonuna tıklandığında THEN POS_Sistemi iade işlemi dialogunu açacaktır
5. WHEN FİŞ YAZDIR butonuna tıklandığında ve satış tamamlandığında THEN POS_Sistemi Fiş yazdıracaktır

### Gereksinim 7

**Kullanıcı Hikayesi:** Bir kasiyer olarak, klavye kısayollarını kullanabilmek istiyorum, böylece mouse kullanmadan hızlı işlem yapabilirim.

#### Kabul Kriterleri

1. WHEN F2 tuşuna basıldığında THEN POS_Sistemi barkod alanına odak verecektir
2. WHEN F4 tuşuna basıldığında THEN POS_Sistemi nakit ödeme işlemini başlatacaktır
3. WHEN F5 tuşuna basıldığında THEN POS_Sistemi kart ödeme işlemini başlatacaktır
4. WHEN ESC tuşuna basıldığında THEN POS_Sistemi onay soracak ve onaylandığında işlemi iptal edecektir
5. WHEN DEL tuşuna basıldığında THEN POS_Sistemi seçili sepet satırını silecektir

### Gereksinim 8

**Kullanıcı Hikayesi:** Bir sistem yöneticisi olarak, POS buton eşleştirmelerini görebilmek istiyorum, böylece sistem entegrasyonunu kontrol edebilirim.

#### Kabul Kriterleri

1. WHEN POS ekranında "Eşleştirmeleri Göster" butonuna tıklandığında THEN POS_Sistemi Eşleştirme_Tablosu popup olarak gösterecektir
2. WHEN Eşleştirme_Tablosu görüntülendiğinde THEN POS_Sistemi Ekran, Buton, Handler, Servis Metodu kolonlarını gösterecektir
3. WHEN herhangi bir POS butonu tıklandığında THEN POS_Sistemi eşleştirme kaydını otomatik güncelleyecektir
4. WHEN Eşleştirme_Tablosu CSV formatında dışa aktarıldığında THEN POS_Sistemi dosyayı başarıyla kaydedecektir
5. WHEN servis metodu mevcut değilse THEN POS_Sistemi "Servis hazır değil" mesajını gösterecek ancak çökmeyecektir

### Gereksinim 9

**Kullanıcı Hikayesi:** Bir geliştirici olarak, POS ekranının modüler yapıda olmasını istiyorum, böylece bakım ve geliştirme kolaylaşsın.

#### Kabul Kriterleri

1. WHEN POS ekranı oluşturulduğunda THEN POS_Sistemi her UI bileşenini ayrı dosyada tanımlayacaktır
2. WHEN dosya boyutu kontrol edildiğinde THEN POS_Sistemi hiçbir dosyanın 120 satırı geçmemesini sağlayacaktır
3. WHEN fonksiyon boyutu kontrol edildiğinde THEN POS_Sistemi hiçbir fonksiyonun 25 satırı geçmemesini sağlayacaktır
4. WHEN kod kalitesi kontrol edildiğinde THEN POS_Sistemi PEP8 standartlarına yüzde yüz uyum sağlayacaktır
5. WHEN UI bileşenleri incelendiğinde THEN POS_Sistemi iş kuralı içermeyecek ve sadece Servis_Katmani çağrıları yapacaktır

### Gereksinim 10

**Kullanıcı Hikayesi:** Bir kullanıcı olarak, POS ekranında hata durumlarında bilgilendirilmek istiyorum, böylece ne yapacağımı bilebilirim.

#### Kabul Kriterleri

1. WHEN Servis_Katmani çağrısı başarısız olduğunda THEN POS_Sistemi QMessageBox ile hata mesajını gösterecektir
2. WHEN hata oluştuğunda THEN POS_Sistemi log dosyasına detaylı hata kaydı yazacaktır
3. WHEN ağ bağlantısı kesildiğinde THEN POS_Sistemi "Bağlantı hatası" mesajını gösterecektir
4. WHEN stok yetersiz olduğunda THEN POS_Sistemi "Stok yetersiz" uyarısını gösterecektir
5. WHEN kritik hata oluştuğunda THEN POS_Sistemi çökmeyecek, hatayı yakalayacak ve kullanıcıyı bilgilendirecektir