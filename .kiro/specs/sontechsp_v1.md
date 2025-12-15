# SPEC: SONTECHSP (ERP + POS + CRM) v1


## 1) Amaç
Windows üzerinde kurulabilen, çoklu mağaza/şube ve çoklu PC ile eş zamanlı çalışan
Hızlı Satış (POS) + ERP + CRM sistemi.


## 2) Kapsam (Var)
- POS: Barkodlu satış, sepet, ödeme (nakit/kart/parçalı), iade, beklet, fiş
- Stok/Envanter: Ürün kartı, çoklu barkod, depo, stok hareketi, sayım, transfer
- CRM: Müşteri kartı, sadakat puanı (temel)
- E-ticaret/Pazaryeri: Çoklu mağaza hesabı, sipariş çekme, stok/fiyat gönderme (altyapı)
- E-belge: e-Fatura/e-Arşiv/e-İrsaliye outbox + durum (altyapı)
- Kargo: Etiket oluşturma + takip (altyapı)
- Raporlar: Satış özeti, kritik stok, en çok satan (temel)
- Kurulum: Klasör oluşturma, DB testi, migration çalıştırma, admin oluşturma


## 3) Kapsam Dışı
- Logo / Mikro entegrasyonu
- Web panel (şimdilik)
- Mobil uygulama (şimdilik)


## 4) Teknik Kararlar (Değişmez)
- Python %90, SQL %10
- Arayüz: PyQt5
- Backend: FastAPI (lokalde servis)
- Veritabanı: PostgreSQL (ana) + SQLite (offline POS)
- ORM: SQLAlchemy, Migration: Alembic
- Paketleme: PyInstaller
- Mimari: Arayüz -> Servis -> Depo (Repository) -> Veritabanı


## 5) Kritik İş Kuralları
- Negatif stok eşiği:
- stok 0’da uyar
- -1..-5 arası uyarıları göster
- -5 altına düşecek satışa izin verme
- Çoklu PC eş zamanlı stok:
- stok düşümünde transaction + row-level lock


## 6) Ekranlar
- Giriş
- Firma/Mağaza/Terminal seçimi
- AnaPencere (sol menü)
- Gösterge Paneli
- POS Satış
- Ürünler/Stok
- Müşteriler
- E-ticaret
- E-Fatura
- Kargo
- Raporlar
- Ayarlar


## 7) Kabul Kriterleri (MVP)
- Aynı üründen 2 PC aynı anda satış denediğinde stok tutarlılığı bozulmayacak.
- POS ödeme tamamlama tek transaction ile:
stok kilitle -> kontrol -> düş -> satış kaydı -> commit
- Offline satış SQLite kuyruğa yazılacak (senkron iskeleti yeter).
- İlk açılış: klasörler + DB test + migration + admin kullanıcı.


## 8) Kilometre Taşları
M1: Çekirdek + Veritabanı + Stok
M2: POS
M3: Arayüz iskeletleri
M4: E-ticaret / E-belge / Kargo altyapı
M5: Kurulum + paketleme
M6: Testler + stabilizasyon

sontechsp/
uygulama/
cekirdek/
veritabani/
modeller/
depolar/
gocler/
moduller/
stok/
pos/
crm/
satis_belgeleri/
eticaret/
ebelge/
kargo/
raporlar/
servisler/
arayuz/
kurulum/
testler/
pyproject.toml
README.md


Minimum Başlangıç Dosyaları

README.md

pyproject.toml

uygulama/__init__.py

uygulama/ana.py

3) Veritabanı Tablo İsimleri (Tam Türkçe)

Aşağıdaki tablo isimleri kesin standarttır.

3.1 Yetki/Kullanıcı

kullanicilar

roller

yetkiler

kullanici_rolleri

rol_yetkileri

3.2 Firma/Mağaza/Terminal

firmalar

magazalar

terminaller

depolar

3.3 Stok

urunler

urun_barkodlari

stok_bakiyeleri

stok_hareketleri

3.4 CRM

musteriler

sadakat_puanlari

3.5 POS

pos_satislar

pos_satis_satirlari

odeme_kayitlari

3.6 Belgeler

satis_belgeleri

satis_belge_satirlari

3.7 E-ticaret

eticaret_hesaplari

eticaret_siparisleri

3.8 E-belge

ebelge_cikis_kuyrugu

ebelge_durumlari

3.9 Kargo

kargo_etiketleri

kargo_takipleri