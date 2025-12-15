# SONTECHSP Çekirdek Altyapı Kullanım Rehberi

## Genel Bakış

SONTECHSP çekirdek altyapısı, uygulamanın temel işlevselliğini sağlayan merkezi bileşenlerden oluşur. Bu rehber, çekirdek altyapı modüllerinin nasıl kullanılacağını açıklar.

## Hızlı Başlangıç

### 1. Sistem Başlatma

```python
from sontechsp.uygulama.cekirdek import cekirdek_baslat, cekirdek_durdur

# Sistemi başlat
if cekirdek_baslat():
    print("Çekirdek sistem başarıyla başlatıldı")
else:
    print("Sistem başlatma hatası")

# Uygulama sonunda sistemi durdur
cekirdek_durdur()
```

### 2. Temel Kullanım

```python
from sontechsp.uygulama.cekirdek import (
    ayarlar_yoneticisi_al,
    kayit_sistemi_al,
    yetki_kontrolcu_al,
    oturum_yoneticisi_al
)

# Ayarlar yöneticisi
ayarlar = ayarlar_yoneticisi_al()
veritabani_url = ayarlar.ayar_oku("VERITABANI_URL")

# Kayıt sistemi
kayit = kayit_sistemi_al()
kayit.info("Uygulama başlatıldı")

# Yetki kontrolü
yetki = yetki_kontrolcu_al()
if yetki.izin_var_mi("admin", "veri_sil"):
    print("Silme izni var")

# Oturum yönetimi
oturum = oturum_yoneticisi_al()
oturum_bilgisi = oturum.oturum_baslat(1, "kullanici", 1, 1)
```

## Modül Detayları

### Ayarlar Yönetimi

#### Temel Kullanım

```python
from sontechsp.uygulama.cekirdek.ayarlar import ayarlar_yoneticisi_al

ayarlar = ayarlar_yoneticisi_al()

# Ayar okuma
log_seviyesi = ayarlar.ayar_oku("LOG_SEVIYESI", "INFO")
veritabani_url = ayarlar.zorunlu_ayar_oku("VERITABANI_URL")

# Ayar doğrulama
try:
    ayarlar.ayar_dogrula()
    print("Tüm zorunlu ayarlar mevcut")
except ValueError as e:
    print(f"Ayar hatası: {e}")

# Örnek dosya oluşturma
ayarlar.ornek_dosya_olustur()
```

#### Yapılandırma Modeli

```python
# Tip güvenli yapılandırma
yapilandirma = ayarlar.yapilandirma_modeli_olustur()
print(f"Ortam: {yapilandirma.ortam}")
print(f"Log klasörü: {yapilandirma.log_klasoru}")
```

#### Dinamik Ayar Değişikliği

```python
# Ayar dosyası değişikliklerini algıla
if ayarlar.ayar_degisikligini_algi():
    print("Ayarlar güncellendi")
    # Gerekli işlemleri yap
```

### Kayıt (Logging) Sistemi

#### Temel Kullanım

```python
from sontechsp.uygulama.cekirdek.kayit import kayit_sistemi_al

kayit = kayit_sistemi_al()

# Farklı seviyelerde log
kayit.debug("Debug mesajı")
kayit.info("Bilgi mesajı")
kayit.warning("Uyarı mesajı")
kayit.error("Hata mesajı")
kayit.critical("Kritik hata")

# Exception ile birlikte log
try:
    # Hata oluşabilecek kod
    pass
except Exception as e:
    kayit.exception("İşlem sırasında hata oluştu")
```

#### Gelişmiş Özellikler

```python
# Log seviyesi değiştirme
kayit.log_seviyesi_degistir("DEBUG")

# Log dosyası bilgileri
print(f"Log dosyası: {kayit.log_dosyasi_yolu()}")
print(f"Dosya boyutu: {kayit.log_dosyasi_boyutu()} byte")

# Log istatistikleri
istatistikler = kayit.log_istatistikleri()
print(f"Toplam dosya sayısı: {istatistikler['dosya_sayisi']}")

# Eski log dosyalarını temizle
silinen_sayisi = kayit.log_temizle(gun_sayisi=30)
print(f"{silinen_sayisi} eski log dosyası silindi")
```

### Hata Yönetimi

#### Hata Sınıfları

```python
from sontechsp.uygulama.cekirdek.hatalar import (
    SontechHatasi, AlanHatasi, DogrulamaHatasi, EntegrasyonHatasi
)

# Alan doğrulama hatası
try:
    if not kullanici_adi:
        raise AlanHatasi("kullanici_adi", "Kullanıcı adı boş olamaz")
except AlanHatasi as e:
    print(f"Alan hatası: {e}")

# Veri doğrulama hatası
try:
    if yas < 0:
        raise DogrulamaHatasi("yas", "Yaş negatif olamaz", yas, "pozitif sayı")
except DogrulamaHatasi as e:
    print(f"Doğrulama hatası: {e}")

# Entegrasyon hatası
try:
    # API çağrısı
    pass
except Exception as e:
    raise EntegrasyonHatasi("api_cagrisi", f"API hatası: {e}", "timeout")
```

### Yetki Kontrolü

#### Temel Kullanım

```python
from sontechsp.uygulama.cekirdek.yetki import yetki_kontrolcu_al, YetkiMatrisi

yetki = yetki_kontrolcu_al()

# Yetki matrisi tanımlama
matris = YetkiMatrisi(
    roller={
        "admin": ["*"],  # Tüm izinler
        "manager": ["veri_oku", "veri_yaz", "rapor_gor"],
        "kullanici": ["veri_oku"]
    },
    varsayilan_roller=["kullanici"],
    admin_rolleri=["admin"]
)

yetki.yetki_matrisi_yukle(matris)

# İzin kontrolü
if yetki.izin_var_mi("manager", "veri_yaz"):
    print("Yazma izni var")

# Çoklu izin kontrolü
izinler = yetki.coklu_izin_var_mi("kullanici", ["veri_oku", "veri_yaz"])
print(izinler)  # {'veri_oku': True, 'veri_yaz': False}
```

#### Gelişmiş Özellikler

```python
# Rol doğrulama
if yetki.rol_dogrula("admin"):
    print("Geçerli rol")

# Rol izinlerini listele
izinler = yetki.rol_izinlerini_listele("manager")
print(f"Manager izinleri: {izinler}")

# İzin gerektiren rolleri bul
roller = yetki.izin_gerektiren_rolleri_listele("veri_sil")
print(f"Silme izni olan roller: {roller}")

# En yüksek rolü bul
en_yuksek = yetki.en_yuksek_rol_bul(["kullanici", "manager", "admin"])
print(f"En yüksek rol: {en_yuksek}")
```

#### Decorator Kullanımı

```python
from sontechsp.uygulama.cekirdek.yetki import yetki_gerekli

@yetki_gerekli("veri_sil")
def veri_sil(rol, veri_id):
    # Silme işlemi
    print(f"Veri {veri_id} silindi")

# Kullanım
try:
    veri_sil("admin", 123)  # Başarılı
    veri_sil("kullanici", 456)  # DogrulamaHatasi fırlatır
except DogrulamaHatasi as e:
    print(f"Yetki hatası: {e}")
```

### Oturum Yönetimi

#### Temel Kullanım

```python
from sontechsp.uygulama.cekirdek.oturum import oturum_yoneticisi_al

oturum = oturum_yoneticisi_al()

# Oturum başlatma
oturum_bilgisi = oturum.oturum_baslat(
    kullanici_id=1,
    kullanici_adi="ahmet",
    firma_id=1,
    magaza_id=1,
    terminal_id=1,
    roller=["manager", "satis"]
)

print(f"Oturum başlatıldı: {oturum_bilgisi.kullanici_adi}")

# Aktif oturum kontrolü
if oturum.oturum_aktif_mi():
    aktif = oturum.aktif_oturum_al()
    print(f"Aktif kullanıcı: {aktif.kullanici_adi}")
```

#### Bağlam Yönetimi

```python
# Bağlam güncelleme
oturum.baglan_guncelle(
    magaza_id=2,
    terminal_id=3
)

# Bağlam bilgisi alma
firma_id = oturum.baglan_bilgisi_al("firma_id")
magaza_id = oturum.baglan_bilgisi_al("magaza_id")

# Ek bilgi ekleme
oturum.baglan_bilgisi_ayarla("son_islem", "satis")
son_islem = oturum.baglan_bilgisi_al("son_islem")
```

#### Çoklu Terminal Desteği

```python
# Terminal listesi tanımlama
terminal_listesi = [1, 2, 3, 4]
oturum.coklu_terminal_destegi(terminal_listesi)

# Terminal değiştirme
oturum.terminal_degistir(2)

# Oturum süre bilgileri
oturum_suresi = oturum.oturum_suresi_al()  # saniye
son_aktivite = oturum.son_aktivite_suresi_al()  # saniye

print(f"Oturum süresi: {oturum_suresi} saniye")
print(f"Son aktivite: {son_aktivite} saniye önce")
```

#### Oturum Sonlandırma

```python
# Oturumu sonlandır
if oturum.oturum_sonlandir():
    print("Oturum başarıyla sonlandırıldı")

# Kontrol
if not oturum.oturum_aktif_mi():
    print("Oturum kapalı")
```

## Kısayol Fonksiyonlar

```python
from sontechsp.uygulama.cekirdek.oturum import (
    aktif_oturum, oturum_baslat, oturum_sonlandir
)

# Hızlı oturum başlatma
oturum_baslat(1, "kullanici", 1, 1)

# Aktif oturum bilgisi
oturum_bilgisi = aktif_oturum()
if oturum_bilgisi:
    print(f"Aktif kullanıcı: {oturum_bilgisi.kullanici_adi}")

# Hızlı sonlandırma
oturum_sonlandir()
```

## Sistem Durumu ve Sağlık Kontrolü

```python
from sontechsp.uygulama.cekirdek import cekirdek_durum, cekirdek_saglik

# Sistem durum bilgileri
durum = cekirdek_durum()
print(f"Sistem başlatıldı: {durum['baslatildi']}")
print(f"Python sürümü: {durum['python_surumu']}")

# Sağlık kontrolü
if cekirdek_saglik():
    print("Sistem sağlıklı")
else:
    print("Sistem sorunu var")
```

## Hata Ayıklama

### Log Seviyesi Ayarlama

```python
# Geliştirme sırasında detaylı loglar
kayit = kayit_sistemi_al()
kayit.log_seviyesi_degistir("DEBUG")

# Sistem bilgilerini logla
kayit.sistem_bilgisi_logla()
```

### Ayar Kontrolü

```python
# Tüm ayarları listele (hassas bilgiler maskelenir)
ayarlar = ayarlar_yoneticisi_al()
tum_ayarlar = ayarlar.tum_ayarlari_listele()
for anahtar, deger in tum_ayarlar.items():
    print(f"{anahtar}: {deger}")
```

### Yetki Sistemi Kontrolü

```python
# Yetki istatistikleri
yetki = yetki_kontrolcu_al()
istatistikler = yetki.yetki_istatistikleri()
print(f"Toplam rol sayısı: {istatistikler['toplam_rol_sayisi']}")
print(f"Toplam izin sayısı: {istatistikler['toplam_izin_sayisi']}")
```

## En İyi Uygulamalar

### 1. Sistem Başlatma Sırası

```python
# Doğru sıra
def uygulama_baslat():
    # 1. Çekirdek sistemi başlat
    if not cekirdek_baslat():
        return False
    
    # 2. Veritabanı bağlantısını test et
    # 3. Diğer servisleri başlat
    # 4. UI'ı başlat
    
    return True
```

### 2. Hata Yönetimi

```python
# Merkezi hata yakalama
def guvenli_islem(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SontechHatasi as e:
            kayit = kayit_sistemi_al()
            kayit.error(f"İş hatası: {e}")
            # Kullanıcıya uygun mesaj göster
        except Exception as e:
            kayit = kayit_sistemi_al()
            kayit.exception(f"Beklenmeyen hata: {e}")
            # Sistem yöneticisine bildir
    return wrapper
```

### 3. Oturum Güvenliği

```python
# Oturum timeout kontrolü
def oturum_kontrol_et():
    oturum = oturum_yoneticisi_al()
    if oturum.oturum_aktif_mi():
        son_aktivite = oturum.son_aktivite_suresi_al()
        if son_aktivite > 3600:  # 1 saat
            oturum.oturum_sonlandir()
            return False
    return True
```

### 4. Performans İpuçları

```python
# Yetki cache'ini kullan
yetki = yetki_kontrolcu_al()
# Cache otomatik olarak kullanılır, manuel temizlik gerekirse:
# yetki.cache_yenile()

# Log seviyesini üretimde optimize et
if ortam == "prod":
    kayit = kayit_sistemi_al()
    kayit.log_seviyesi_degistir("WARNING")
```

## Sorun Giderme

### Yaygın Hatalar

1. **Import Hatası**: Modül bulunamıyor
   ```python
   # Çözüm: PYTHONPATH'i kontrol et
   import sys
   sys.path.append('/path/to/sontechsp')
   ```

2. **Ayar Hatası**: Zorunlu ayar eksik
   ```python
   # Çözüm: .env dosyasını kontrol et
   ayarlar = ayarlar_yoneticisi_al()
   ayarlar.ornek_dosya_olustur()  # Örnek dosya oluştur
   ```

3. **Log Hatası**: Log klasörü oluşturulamıyor
   ```python
   # Çözüm: Klasör izinlerini kontrol et
   import os
   os.makedirs("logs", exist_ok=True)
   ```

### Debug Modu

```python
# Debug modunu aktifleştir
import os
os.environ["LOG_SEVIYESI"] = "DEBUG"
os.environ["ORTAM"] = "dev"

# Sistemi yeniden başlat
cekirdek_durdur()
cekirdek_baslat()
```

Bu rehber, SONTECHSP çekirdek altyapısının temel kullanımını kapsar. Daha detaylı bilgi için kaynak kodundaki docstring'leri inceleyebilirsiniz.