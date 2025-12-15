PROJE MASTER KURALLARI (DEĞİŞMEZ)

AMAÇ
Windows üzerinde çalışacak, kurulabilir (installer), çoklu mağaza/şube, çoklu PC eş zamanlı çalışan
POS + ERP + CRM sistemi geliştiriyoruz.
Entegrasyonlar: e-ticaret siteleri, pazaryerleri, e-Fatura/e-Arşiv/e-İrsaliye (özel entegratör), kargo.
Logo/Mikro entegrasyonu YOK.

TEKNOLOJİ (DEĞİŞMEZ)
- Python %90, SQL %10
- GUI: PyQt6
- Backend: FastAPI (lokalde servis)
- DB: PostgreSQL (ana) + SQLite (POS offline cache)
- ORM: SQLAlchemy, Migration: Alembic
- Paketleme: PyInstaller (Windows)

MİMARİ (DEĞİŞMEZ)
- Katmanlar: UI(PYQT) -> Service -> Repository -> DB
- UI içinde iş kuralı YASAK
- DB erişimi sadece repository katmanında
- Çoklu PC stok tutarlılığı: PostgreSQL transaction + row-level lock
- Offline POS: SQLite kuyruk + senkron servis iskeleti

KODLAMA KURALLARI (ZORUNLU)
- PEP8 zorunlu
- Tek dosya maksimum 120 satır (yorumlar hariç)
- Fonksiyon maksimum 25 satır (gerekirse böl)
- Parça parça çıktı YASAK: güncellediğin her dosyayı TAM ver
- Her dosyanın başına sürüm başlığı koy:
  # Version: 0.1.0
  # Last Update: YYYY-MM-DD
  # Module: <module_name>
  # Description: <short>
  # Changelog:
  # - <madde>

ÇIKTI PROTOKOLÜ (ZORUNLU)
1) Önce "Değişecek/Oluşacak dosyalar:" listesini ver.
2) Sonra her dosyayı ayrı ayrı şu formatla ver:
   --- FILE: path/to/file.py ---
   <tam dosya içeriği>
3) Kod dışında gereksiz açıklama yazma.
4) Eksik bilgi varsa varsayım yap ama varsayımı tek cümle ile belirt.

SAĞLAMLIK
- Kritik işlemlerde hata yönetimi + log
- DB işlemleri transaction’lı
- Veri tutarlılığı performanstan önce gelir

---
inclusion: always
---
<!------------------------------------------------------------------------------------
   Add rules to this file or a short description and have Kiro refine them for you.
   
   Learn about inclusion modes: https://kiro.dev/docs/steering/#inclusion-modes
-------------------------------------------------------------------------------------> 