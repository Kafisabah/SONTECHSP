# Kod Kalitesi Refactoring Uygulama Tasarımı

## Genel Bakış

Bu tasarım dokümanı, kod kalitesi analizi sonuçlarına dayanarak tespit edilen sorunların sistematik çözümü için refactoring stratejisini tanımlar. Güvenlik öncelikli, adım adım yaklaşım benimsenmiştir.

## Mimari Tasarım

### Refactoring Süreci Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    Refactoring Orkestratörü                 │
├─────────────────────────────────────────────────────────────┤
│  1. Analiz ve Planlama                                      │
│  2. Güvenlik ve Yedekleme                                   │
│  3. Dosya/Fonksiyon Bölme                                   │
│  4. Import Güncelleme                                       │
│  5. Test Doğrulama                                          │
│  6. Kullanıcı Onayı                                         │
└─────────────────────────────────────────────────────────────┘
```

### Katman Yapısı

```
refactoring_uygulama/
├── orkestrator/           # Ana koordinasyon
│   ├── refactoring_yoneticisi.py
│   ├── faz_kontrolcusu.py
│   └── ilerleme_takipcisi.py
├── analizorler/           # Analiz araçları
│   ├── dosya_analizoru.py
│   ├── bagimlilik_analizoru.py
│   └── etki_analizoru.py
├── boluculer/             # Bölme araçları
│   ├── ui_dosya_bolucu.py
│   ├── repository_bolucu.py
│   ├── servis_bolucu.py
│   └── fonksiyon_bolucu.py
├── guncelleyiciler/       # Güncelleme araçları
│   ├── import_guncelleyici.py
│   ├── test_guncelleyici.py
│   └── referans_guncelleyici.py
├── dogrulayicilar/        # Doğrulama araçları
│   ├── fonksiyonalite_dogrulayici.py
│   ├── test_dogrulayici.py
│   └── mimari_dogrulayici.py
└── guvenlik/              # Güvenlik araçları
    ├── yedek_yoneticisi.py
    ├── geri_alma_yoneticisi.py
    └── denetim_kaydedici.py
```

## Detaylı Tasarım

### 1. Refactoring Yöneticisi (Ana Koordinatör)

```python
class RefactoringYoneticisi:
    """Ana refactoring sürecini yöneten sınıf"""
    
    def __init__(self):
        self.yedek_yoneticisi = YedekYoneticisi()
        self.faz_kontrolcusu = FazKontrolcusu()
        self.ilerleme_takipcisi = IlerlemeTakipcisi()
        self.denetim_kaydedici = DenetimKaydedici()
    
    def refactoring_plani_uygula(self, plan: RefactoringPlani) -> RefactoringSonucu:
        """Refactoring planını güvenli şekilde uygular"""
        # 1. Yedek oluştur
        # 2. Fazları sırayla çalıştır
        # 3. Her adımda doğrulama yap
        # 4. Hata durumunda geri al
        pass
```

### 2. Faz Kontrolcüsü

```python
class FazKontrolcusu:
    """Refactoring fazlarını kontrol eden sınıf"""
    
    FAZLAR = [
        "UI_KATMANI_REFACTORING",        # UI katmanı refactoring
        "REPOSITORY_KATMANI_REFACTORING", # Repository katmanı refactoring
        "SERVIS_KATMANI_REFACTORING",    # Servis katmanı refactoring
        "ARACLAR_REFACTORING"            # Araçlar refactoring
    ]
    
    def faz_calistir(self, faz: str, hedefler: List[str]) -> FazSonucu:
        """Belirli bir fazı güvenli şekilde çalıştırır"""
        pass
```

### 3. UI Dosya Bölücü

```python
class UIDosyaBolucu:
    """UI dosyalarını mantıklı modüllere bölen sınıf"""
    
    def ebelge_dosyasi_bol(self, dosya_yolu: str) -> BolmeSonucu:
        """ebelge.py dosyasını böler"""
        # Hedef yapı:
        # ebelge/
        # ├── __init__.py
        # ├── ebelge_ana.py          # Ana ekran (150 satır)
        # ├── ebelge_filtreleri.py   # filtre_grubu_olustur (106 satır)
        # ├── ebelge_islemleri.py    # islemler_grubu_olustur (110 satır)
        # ├── ebelge_durum.py        # durum_bilgisi_grubu_olustur (67 satır)
        # └── ebelge_tablolar.py     # tablo güncelleme fonksiyonları
        pass
    
    def raporlar_dosyasi_bol(self, dosya_yolu: str) -> BolmeSonucu:
        """raporlar.py dosyasını böler"""
        # Hedef yapı:
        # raporlar/
        # ├── __init__.py
        # ├── rapor_ana.py           # Ana ekran
        # ├── rapor_olusturma.py     # rapor_olusturma_grubu_olustur (113 satır)
        # ├── rapor_filtreleri.py    # filtre fonksiyonları
        # └── rapor_export.py        # dışa aktarma fonksiyonları
        pass
```

### 4. Fonksiyon Bölücü

```python
class FonksiyonBolucu:
    """Büyük fonksiyonları bölen sınıf"""
    
    def buyuk_fonksiyon_bol(self, dosya_yolu: str, fonksiyon_adi: str) -> BolmeSonucu:
        """Büyük fonksiyonu yardımcı fonksiyonlara böler"""
        # Örnek: transfer_yap (143 satır) → 
        # - transfer_yap (25 satır - ana koordinasyon)
        # - _transfer_dogrula (30 satır)
        # - _stok_rezerve_et (35 satır)
        # - _transfer_kaydet (30 satır)
        # - _bildirim_gonder (23 satır)
        pass
```

## Refactoring Stratejileri

### 1. UI Dosyası Bölme Stratejisi

#### ebelge.py Bölme Planı (805 → ~300 satır)

```python
# Mevcut yapı analizi:
# - filtre_grubu_olustur: 106 satır
# - islemler_grubu_olustur: 110 satır  
# - durum_bilgisi_grubu_olustur: 67 satır
# - Diğer fonksiyonlar: ~522 satır

# Hedef yapı:
ebelge/
├── __init__.py                 # Public API export
├── ebelge_ana.py              # Ana ekran sınıfı (150 satır)
├── ebelge_filtreleri.py       # Filtre UI bileşenleri (120 satır)
├── ebelge_islemleri.py        # İşlem butonları ve handler'lar (130 satır)
├── ebelge_durum.py            # Durum gösterimi (80 satır)
└── ebelge_yardimcilar.py      # Yardımcı fonksiyonlar (100 satır)
```

#### Bölme Algoritması

```python
def ui_dosya_bolme_algoritmasi(dosya_yolu: str) -> BolmePlani:
    """UI dosyası bölme algoritması"""
    
    # 1. AST analizi ile fonksiyonları grupla
    fonksiyonlar = fonksiyonlari_analiz_et(dosya_yolu)
    
    # 2. Fonksiyonel gruplama
    gruplar = {
        'ana_ekran': [],      # Ana sınıf ve __init__
        'filtreler': [],      # Filtre ile ilgili fonksiyonlar
        'islemler': [],       # İşlem butonları ve handler'lar
        'durum': [],          # Durum gösterimi
        'yardimcilar': []     # Yardımcı fonksiyonlar
    }
    
    # 3. Fonksiyonları gruplara ata
    for fonksiyon in fonksiyonlar:
        grup = fonksiyon_grubunu_belirle(fonksiyon)
        gruplar[grup].append(fonksiyon)
    
    # 4. Her grup için ayrı dosya oluştur
    bolme_plani = bolme_plani_olustur(gruplar)
    
    return bolme_plani
```

### 2. Repository Bölme Stratejisi

#### satis_repository.py Bölme Planı (501 → ~200 satır)

```python
# Hedef yapı:
satis_repository/
├── __init__.py                    # Public API
├── satis_crud.py                  # Temel CRUD işlemleri (120 satır)
├── satis_sorgular.py              # Karmaşık sorgular (150 satır)  
├── satis_raporlar.py              # Rapor sorguları (120 satır)
└── satis_yardimcilar.py           # Yardımcı fonksiyonlar (80 satır)
```

### 3. Fonksiyon Bölme Stratejisi

#### transfer_yap Fonksiyonu Bölme Planı (143 → 25 satır)

```python
# Mevcut: tek fonksiyon 143 satır
def transfer_yap(self, kaynak_magaza_id, hedef_magaza_id, urun_id, miktar):
    # 143 satır kod...

# Hedef: ana fonksiyon + yardımcılar
def transfer_yap(self, kaynak_magaza_id, hedef_magaza_id, urun_id, miktar):
    """Ana transfer koordinasyon fonksiyonu (25 satır)"""
    # 1. Doğrulama
    self._transfer_dogrula(kaynak_magaza_id, hedef_magaza_id, urun_id, miktar)
    
    # 2. Stok rezervasyonu
    rezervasyon = self._stok_rezerve_et(kaynak_magaza_id, urun_id, miktar)
    
    # 3. Transfer kaydı
    transfer_id = self._transfer_kaydet(kaynak_magaza_id, hedef_magaza_id, urun_id, miktar)
    
    # 4. Bildirim
    self._bildirim_gonder(transfer_id)
    
    return transfer_id

def _transfer_dogrula(self, kaynak_magaza_id, hedef_magaza_id, urun_id, miktar):
    """Transfer doğrulama işlemleri (30 satır)"""
    pass

def _stok_rezerve_et(self, kaynak_magaza_id, urun_id, miktar):
    """Stok rezervasyon işlemleri (35 satır)"""
    pass

def _transfer_kaydet(self, kaynak_magaza_id, hedef_magaza_id, urun_id, miktar):
    """Transfer kayıt işlemleri (30 satır)"""
    pass

def _bildirim_gonder(self, transfer_id):
    """Bildirim gönderme işlemleri (23 satır)"""
    pass
```

## Güvenlik ve Geri Alma Tasarımı

### Yedekleme Stratejisi

```python
class YedekYoneticisi:
    """Güvenli yedekleme yönetimi"""
    
    def yedek_olustur(self, dosyalar: List[str]) -> YedekBilgisi:
        """Dosyalar için yedek oluşturur"""
        yedek_id = yedek_id_uret()
        yedek_yolu = f"guvenlik/yedekler/{yedek_id}"
        
        # 1. Git commit oluştur
        git_commit = git_commit_olustur(dosyalar)
        
        # 2. Dosya kopyaları oluştur
        dosya_kopyalari = dosyalari_yedekle(dosyalar, yedek_yolu)
        
        # 3. Metadata kaydet
        metadata = YedekMetadata(
            yedek_id=yedek_id,
            zaman_damgasi=datetime.now(),
            dosyalar=dosyalar,
            git_commit=git_commit,
            dosya_kopyalari=dosya_kopyalari
        )
        
        yedek_metadata_kaydet(metadata)
        return YedekBilgisi(yedek_id, metadata)
```

## Sonuç

Bu tasarım, kod kalitesi sorunlarının güvenli ve sistematik çözümü için kapsamlı bir yaklaşım sunar. Güvenlik öncelikli yaklaşım, adım adım uygulama ve kapsamlı doğrulama mekanizmaları ile risk minimize edilmiştir.

### Başarı Kriterleri
- 106 dosyadan 30'a düşüş (%70 azalma)
- 544 fonksiyondan 220'ye düşüş (%60 azalma)
- Tüm testlerin geçmesi
- UI fonksiyonalitesinin korunması
- Performans kaybının %5'in altında kalması