# Ayarlar.py Dosyası Bölme Planı

## Mevcut Durum Analizi
- **Dosya:** `uygulama/arayuz/ekranlar/ayarlar.py`
- **Toplam Satır:** 928 satır
- **Hedef:** 120 satır limitine uygun modüllere bölme

## Tespit Edilen Büyük Fonksiyonlar

### 1. alt_butonlar_olustur() - ~105 satır (217-322)
- Varsayılana dön, içe aktar, dışa aktar, iptal, kaydet butonları
- Event handler bağlantıları
- Stil tanımlamaları

### 2. Sayfa Oluşturma Fonksiyonları (Her biri 40-80 satır)
- genel_ayarlar_sayfasi_olustur()
- veritabani_ayarlar_sayfasi_olustur() 
- pos_ayarlar_sayfasi_olustur()
- stok_ayarlar_sayfasi_olustur()
- eticaret_ayarlar_sayfasi_olustur()
- ebelge_ayarlar_sayfasi_olustur()
- kargo_ayarlar_sayfasi_olustur()
- kullanici_ayarlar_sayfasi_olustur()
- yetki_ayarlar_sayfasi_olustur()
- rapor_ayarlar_sayfasi_olustur()
- sistem_ayarlar_sayfasi_olustur()
- yedekleme_ayarlar_sayfasi_olustur()

### 3. Event Handler Fonksiyonları
- ayarlari_kaydet()
- varsayilana_don()
- ice_aktar()
- disa_aktar()
- degisiklikleri_iptal()

## Önerilen Bölme Yapısı

```
ayarlar/
├── __init__.py                    # Public API export
├── ayar_ana.py                   # Ana ekran sınıfı (150 satır)
├── ayar_butonlari.py             # Alt butonlar ve event handler'lar (120 satır)
├── ayar_formlari.py              # Form sayfaları oluşturma (300 satır)
├── ayar_dogrulama.py             # Doğrulama ve kaydetme işlemleri (100 satır)
└── ayar_yardimcilar.py           # Yardımcı fonksiyonlar (80 satır)
```

## Fonksiyonel Gruplama

### Grup 1: Ana Ekran (ayar_ana.py)
- Ayarlar sınıfı tanımı
- ekrani_hazirla()
- sol_panel_olustur()
- sag_panel_olustur()
- durum_bilgisi_grubu_olustur()
- kategori_degisti()

### Grup 2: Butonlar (ayar_butonlari.py)
- alt_butonlar_olustur()
- varsayilana_don()
- ice_aktar()
- disa_aktar()
- degisiklikleri_iptal()

### Grup 3: Form Sayfaları (ayar_formlari.py)
- Tüm *_sayfasi_olustur() fonksiyonları
- grup_stili()

### Grup 4: Doğrulama (ayar_dogrulama.py)
- ayarlari_kaydet()
- baglanti_test()
- degisiklik_sayisini_guncelle()
- islem_baslat()
- islem_bitir()

### Grup 5: Yardımcılar (ayar_yardimcilar.py)
- verileri_yukle()
- verileri_temizle()
- Diğer yardımcı fonksiyonlar

## Bağımlılık Analizi

### Import'lar
- PyQt6 widget'ları
- TemelEkran base class
- ServisFabrikasi
- UIYardimcilari

### Sınıf Değişkenleri
- kategori_listesi
- icerik_stack
- durum_label
- progress_bar
- degisiklikler dict

## Risk Analizi

### Yüksek Risk
- UI bileşenlerinin bozulması
- Event handler bağlantılarının kopması
- Stil tanımlamalarının kaybolması

### Orta Risk
- Import yapısının karışması
- Sınıf değişkenlerinin erişim sorunu

### Düşük Risk
- Fonksiyon adlandırma çakışması

## Uygulama Stratejisi

1. **Adım 1:** Yedek al
2. **Adım 2:** ayar_butonlari.py oluştur (alt_butonlar_olustur taşı)
3. **Adım 3:** ayar_formlari.py oluştur (sayfa fonksiyonları taşı)
4. **Adım 4:** ayar_dogrulama.py oluştur (doğrulama fonksiyonları taşı)
5. **Adım 5:** ayar_ana.py optimize et
6. **Adım 6:** __init__.py ile API export et
7. **Adım 7:** Test ve doğrulama

## Başarı Kriterleri

- [ ] Her modül 120 satırın altında
- [ ] UI fonksiyonalitesi korunmuş
- [ ] Tüm testler geçiyor
- [ ] Import yapısı temiz
- [ ] Event handler'lar çalışıyor