# POS Yeni Ekran Tasarımı - Gereksinimler Belgesi

## Giriş

Bu belge, SONTECHSP sisteminde POS (Point of Sale) ekranının tamamen yeniden tasarlanması için gereksinimleri tanımlar. Mevcut POS ekranı kasiyer akışına uygun değil, sepet küçük, boş alanlar çok ve ödeme akışı dağınık durumda. Bu tasarım iptal edilerek, hızlı, okunaklı ve kasiyer akışına uygun yeni bir ekran tasarlanacak.

## Sözlük

- **AnaPencere**: Ana uygulama penceresi, tüm modül ekranlarını barındıran container
- **POS_Sistemi**: Point of Sale - Satış noktası sistemi
- **Sepet**: Müşteri alışveriş sepeti, satış öncesi ürün listesi
- **Barkod**: Ürün tanımlama kodu
- **Kasiyer**: Satış işlemini gerçekleştiren kullanıcı
- **Ust_Bar**: Ekranın en üstündeki tam genişlik çubuğu
- **Orta_Alan**: Ana çalışma alanı, sepet ve ödeme panellerini içerir
- **Alt_Serit**: Ekranın altındaki hızlı işlem butonları şeridi
- **QTableView**: PyQt6 tablo widget'ı, model-view mimarisi kullanır
- **QAbstractTableModel**: Tablo verisi için model sınıfı
- **Hizli_Urun_Sekmesi**: Sağ panelde ödeme ile birlikte sekme sistemi
- **Parcali_Odeme**: Nakit ve kart karışık ödeme türü
- **Acik_Hesap**: Müşteri hesabına borç kaydı ile ödeme
- **Turkuaz_Tema**: Ana renk teması (turkuaz, gri, beyaz tonları)

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Bir kasiyer olarak, POS ekranının üst barında tüm temel giriş alanlarına erişebilmek istiyorum, böylece hızlı ürün ekleme ve müşteri işlemleri yapabilirim.

#### Kabul Kriterleri

1. WHEN POS ekranı açıldığında THEN POS_Sistemi tam genişlik Ust_Bar gösterecektir
2. WHEN Ust_Bar görüntülendiğinde THEN POS_Sistemi sol tarafta barkod giriş alanını gösterecektir
3. WHEN Ust_Bar görüntülendiğinde THEN POS_Sistemi barkod alanının yanında ürün arama alanını gösterecektir
4. WHEN Ust_Bar görüntülendiğinde THEN POS_Sistemi sağ tarafta kasiyer/mağaza/terminal etiketini gösterecektir
5. WHEN Ust_Bar görüntülendiğinde THEN POS_Sistemi sağda Müşteri Seç, Müşteri Temizle, Açık Hesap butonlarını gösterecektir

### Gereksinim 2

**Kullanıcı Hikayesi:** Bir kasiyer olarak, barkod ve ürün arama işlemlerini hızlı yapabilmek istiyorum, böylece satış sürecini hızlandırabilirim.

#### Kabul Kriterleri

1. WHEN barkod alanına kod girilip Enter tuşuna basıldığında THEN POS_Sistemi ürünü sepete ekleyecektir
2. WHEN ürün arama alanına metin girildiğinde THEN POS_Sistemi hızlı sonuç dropdown gösterecektir
3. WHEN F2 tuşuna basıldığında THEN POS_Sistemi barkod alanına odak verecektir
4. WHEN geçersiz barkod girildiğinde THEN POS_Sistemi turkuaz renkli hata mesajı gösterecektir
5. WHEN ürün arama sonucundan seçim yapıldığında THEN POS_Sistemi seçilen ürünü sepete ekleyecektir

### Gereksinim 3

**Kullanıcı Hikayesi:** Bir kasiyer olarak, sepeti ana alan olarak görebilmek istiyorum, böylece ürünleri rahatça kontrol edebilirim.

#### Kabul Kriterleri

1. WHEN Orta_Alan görüntülendiğinde THEN POS_Sistemi sol tarafta yüzde 70 genişlikte sepet alanını gösterecektir
2. WHEN sepet alanı görüntülendiğinde THEN POS_Sistemi QTableView ile Barkod, Ürün, Adet, Fiyat, Tutar, Sil kolonlarını gösterecektir
3. WHEN sepet satırı seçildiğinde THEN POS_Sistemi artı/eksi butonları ile adet değiştirme imkanı sunacaktır
4. WHEN DEL tuşuna basıldığında THEN POS_Sistemi seçili satırı silecektir
5. WHEN sepet altında THEN POS_Sistemi Not, İndirim, Kupon butonlarını gösterecektir

### Gereksinim 4

**Kullanıcı Hikayesi:** Bir kasiyer olarak, ödeme panelini sepet yanında görebilmek istiyorum, böylece toplam tutarı takip edebilirim.

#### Kabul Kriterleri

1. WHEN Orta_Alan görüntülendiğinde THEN POS_Sistemi sağ tarafta yüzde 30 genişlikte ödeme panelini gösterecektir
2. WHEN ödeme paneli görüntülendiğinde THEN POS_Sistemi büyük fontla Genel Toplam gösterecektir
3. WHEN ödeme paneli görüntülendiğinde THEN POS_Sistemi Ara Toplam, İndirim, KDV toplamını gösterecektir
4. WHEN ödeme paneli görüntülendiğinde THEN POS_Sistemi NAKİT F4, KART F5, PARÇALI F6, AÇIK HESAP F7 butonlarını gösterecektir
5. WHEN nakit ödeme seçildiğinde THEN POS_Sistemi alınan tutar kutusu ve para üstü hesaplamasını gösterecektir

### Gereksinim 5

**Kullanıcı Hikayesi:** Bir kasiyer olarak, hızlı işlem butonlarını her zaman erişilebilir görmek istiyorum, böylece bekletme ve iade işlemlerini hızla yapabilirim.

#### Kabul Kriterleri

1. WHEN POS ekranı görüntülendiğinde THEN POS_Sistemi Alt_Serit'i tam genişlikte gösterecektir
2. WHEN Alt_Serit görüntülendiğinde THEN POS_Sistemi BEKLET F8, BEKLEYENLER F9, İADE F10, İPTAL ESC, FİŞ YAZDIR, FATURA butonlarını gösterecektir
3. WHEN Alt_Serit görüntülendiğinde THEN POS_Sistemi butonları tek satırda ve her zaman görünür olacak şekilde gösterecektir
4. WHEN BEKLET butonuna tıklandığında THEN POS_Sistemi mevcut sepeti bekletecek ve yeni sepet başlatacaktır
5. WHEN İADE butonuna tıklandığında THEN POS_Sistemi iade işlemi dialogunu açacaktır

### Gereksinim 6

**Kullanıcı Hikayesi:** Bir kasiyer olarak, hızlı ürün butonlarını sepeti küçültmeden kullanabilmek istiyorum, böylece hem sepeti hem hızlı ürünleri görebilirim.

#### Kabul Kriterleri

1. WHEN ödeme paneli görüntülendiğinde THEN POS_Sistemi Ödeme ve Hızlı Ürünler sekmelerini gösterecektir
2. WHEN Hızlı Ürünler sekmesi seçildiğinde THEN POS_Sistemi 12-24 arası ürün butonunu grid halinde gösterecektir
3. WHEN Hızlı Ürünler sekmesi görüntülendiğinde THEN POS_Sistemi kategori dropdown menüsünü gösterecektir
4. WHEN hızlı ürün butonuna tıklandığında THEN POS_Sistemi ürünü sepete ekleyecektir
5. WHEN kategori değiştirildiğinde THEN POS_Sistemi butonları yeni kategori ürünleri ile güncelleyecektir

### Gereksinim 7

**Kullanıcı Hikayesi:** Bir kasiyer olarak, farklı ödeme türlerini kolayca seçebilmek istiyorum, böylece müşteri tercihine göre hızla işlem yapabilirim.

#### Kabul Kriterleri

1. WHEN F4 tuşuna basıldığında THEN POS_Sistemi nakit ödeme işlemini başlatacaktır
2. WHEN F5 tuşuna basıldığında THEN POS_Sistemi kart ödeme işlemini başlatacaktır
3. WHEN F6 tuşuna basıldığında THEN POS_Sistemi Parcali_Odeme dialogunu açacaktır
4. WHEN F7 tuşuna basıldığında THEN POS_Sistemi Acik_Hesap ödeme kontrolü yapacaktır
5. WHEN parçalı ödeme dialogu açıldığında THEN POS_Sistemi nakit ve kart tutar girişi alanlarını gösterecektir

### Gereksinim 8

**Kullanıcı Hikayesi:** Bir kasiyer olarak, klavye kısayollarını kullanarak hızlı çalışabilmek istiyorum, böylece mouse kullanmadan işlem yapabilirim.

#### Kabul Kriterleri

1. WHEN F8 tuşuna basıldığında THEN POS_Sistemi sepet bekletme işlemini gerçekleştirecektir
2. WHEN F9 tuşuna basıldığında THEN POS_Sistemi bekletilen sepetler listesini gösterecektir
3. WHEN F10 tuşuna basıldığında THEN POS_Sistemi iade işlemi dialogunu açacaktır
4. WHEN ESC tuşuna basıldığında THEN POS_Sistemi onay soracak ve işlemi iptal edecektir
5. WHEN artı/eksi tuşlarına basıldığında THEN POS_Sistemi seçili ürünün adetini değiştirecektir

### Gereksinim 9

**Kullanıcı Hikayesi:** Bir kullanıcı olarak, POS ekranının turkuaz-gri tema ile modern görünmesini istiyorum, böylece göz yorucu olmayan bir arayüz kullanabilirim.

#### Kabul Kriterleri

1. WHEN POS ekranı görüntülendiğinde THEN POS_Sistemi Turkuaz_Tema renklerini kullanacaktır
2. WHEN butonlar görüntülendiğinde THEN POS_Sistemi büyük, net ve tek satır butonları gösterecektir
3. WHEN tablo görüntülendiğinde THEN POS_Sistemi satır yüksekliğini artırılmış ve seçili satırı belirgin gösterecektir
4. WHEN paneller görüntülendiğinde THEN POS_Sistemi QFrame ile belirgin kartlar ve uygun spacing gösterecektir
5. WHEN toplam tutarlar görüntülendiğinde THEN POS_Sistemi büyük font ile vurgulanmış gösterecektir

### Gereksinim 10

**Kullanıcı Hikayesi:** Bir geliştirici olarak, POS ekranının modüler yapıda olmasını istiyorum, böylece bakım ve geliştirme kolaylaşsın.

#### Kabul Kriterleri

1. WHEN POS dosyaları oluşturulduğunda THEN POS_Sistemi her bileşeni ayrı dosyada tanımlayacaktır
2. WHEN dosya boyutu kontrol edildiğinde THEN POS_Sistemi hiçbir dosyanın 120 satırı geçmemesini sağlayacaktır
3. WHEN fonksiyon boyutu kontrol edildiğinde THEN POS_Sistemi hiçbir fonksiyonun 25 satırı geçmemesini sağlayacaktır
4. WHEN kod kalitesi kontrol edildiğinde THEN POS_Sistemi PEP8 standartlarına uyum sağlayacaktır
5. WHEN UI bileşenleri incelendiğinde THEN POS_Sistemi iş kuralı içermeyecek ve sadece servis çağrıları yapacaktır

### Gereksinim 11

**Kullanıcı Hikayesi:** Bir kullanıcı olarak, POS ekranında hata durumlarında bilgilendirilmek istiyorum, böylece ne yapacağımı bilebilirim.

#### Kabul Kriterleri

1. WHEN servis çağrısı başarısız olduğunda THEN POS_Sistemi turkuaz renkli hata mesajını gösterecektir
2. WHEN hata oluştuğunda THEN POS_Sistemi log dosyasına detaylı hata kaydı yazacaktır
3. WHEN ağ bağlantısı kesildiğinde THEN POS_Sistemi "Bağlantı hatası" mesajını gösterecektir
4. WHEN stok yetersiz olduğunda THEN POS_Sistemi "Stok yetersiz" uyarısını gösterecektir
5. WHEN kritik hata oluştuğunda THEN POS_Sistemi çökmeyecek ve kullanıcıyı bilgilendirecektir

### Gereksinim 12

**Kullanıcı Hikayesi:** Bir sistem yöneticisi olarak, POS ekranının AnaPencere'ye entegre olmasını istiyorum, böylece diğer modüllerle birlikte çalışabilsin.

#### Kabul Kriterleri

1. WHEN AnaPencere menüsünde "POS Satış" tıklandığında THEN POS_Sistemi yeni tasarım ekranını açacaktır
2. WHEN mevcut eski POS widget'ı varsa THEN POS_Sistemi yönlendirme yapacak ve eski tasarımı kaldıracaktır
3. WHEN menü geçişleri yapıldığında THEN POS_Sistemi ekran durumunu koruyacaktır
4. WHEN uygulama yeniden başlatıldığında THEN POS_Sistemi varsayılan dashboard ekranını gösterecektir
5. WHEN POS ekranı kapatıldığında THEN POS_Sistemi mevcut sepet verilerini güvenli şekilde saklayacaktır