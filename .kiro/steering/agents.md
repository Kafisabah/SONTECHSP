AJAN ROLLERİ (NE YAPAR / NE YAPMAZ)

architect_agent
- YAPAR: dosya/klasör yapısı, modül sınırları, DTO/servis sözleşmeleri, akış haritaları
- YAPMAZ: kod yazmak, SQL yazmak, PyQt ekran kodu

db_agent
- YAPAR: SQLAlchemy modeller, Alembic migration, index/constraint, performans sorguları
- YAPMAZ: UI ve iş akışı kodu

core_agent
- YAPAR: config, logging, errors, permissions, session, ortak yardımcılar
- YAPMAZ: pos/stock/crm iş kuralları

stock_agent
- YAPAR: ürün, barkod, stok hareketi, sayım, transfer, kritik stok, negatif stok eşiği
- YAPMAZ: UI çizmek, e-fatura/kargo entegrasyonu

pos_agent
- YAPAR: sepet, ödeme, iade, beklet, fiş; offline kuyruk iskeleti
- YAPMAZ: e-fatura/kargo API kodu

crm_agent
- YAPAR: müşteri, sadakat, segment temel
- YAPMAZ: POS ödeme ve stok düşüm mantığı

salesdocs_agent
- YAPAR: sipariş/irsaliye/fatura belgeleri ve durum akışı
- YAPMAZ: e-fatura sağlayıcı entegrasyonu, kargo

ecommerce_agent
- YAPAR: pazaryeri/e-ticaret senkron altyapısı (connector interface + job runner)
- YAPMAZ: POS satış, e-fatura XML

einvoice_agent
- YAPAR: e-belge outbox, provider interface, status sync, retry
- YAPMAZ: stok/POS iş kuralları

shipping_agent
- YAPAR: kargo carrier interface, etiket oluşturma, takip senkronu
- YAPMAZ: e-fatura

reporting_agent
- YAPAR: rapor query layer + servisler + export (CSV/PDF temel)
- YAPMAZ: UI tasarımı

ui_agent
- YAPAR: PyQt ekran iskeletleri, navigasyon, signal/slot; sadece service çağırır
- YAPMAZ: iş kuralı/DB sorgusu

installer_agent
- YAPAR: klasör oluşturma, DB test, migration çalıştırma, admin oluşturma, PyInstaller build adımı
- YAPMAZ: pos/stock/crm iş kuralları

qa_agent
- YAPAR: testler ve senaryolar
- YAPMAZ: yeni özellik tasarlamak

---
inclusion: always
---
<!------------------------------------------------------------------------------------
   Add rules to this file or a short description and have Kiro refine them for you.
   
   Learn about inclusion modes: https://kiro.dev/docs/steering/#inclusion-modes
-------------------------------------------------------------------------------------> 