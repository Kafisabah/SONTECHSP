# Version: 0.2.0
# Last Update: 2024-12-17
# Module: crm.depolar
# Description: CRM modülü repository katmanı
# Changelog:
# - İlk oluşturma
# - v0.2.0: Public API export'u tamamlandı, dokümantasyon güncellendi

"""
SONTECHSP CRM Repository Katmanı

Bu katman CRM modülünün veri erişim katmanını içerir:
- Müşteri repository'leri (MusteriDeposu)
- Sadakat puanı repository'leri (SadakatDeposu)

Katman kuralları:
- Servis katmanından çağrılır
- Veritabanı erişimini yönetir
- CRUD işlemlerini gerçekleştirir
- Müşteri veri bütünlüğünü sağlar
- SQLAlchemy ORM kullanır
- Transaction yönetimi yapar

Kullanım Örneği:
    from sontechsp.uygulama.moduller.crm.depolar import MusteriDeposu, SadakatDeposu
    
    # Müşteri deposu kullanımı
    musteri_deposu = MusteriDeposu(db_session)
    musteri = musteri_deposu.musteri_olustur(dto)
    
    # Sadakat deposu kullanımı
    sadakat_deposu = SadakatDeposu(db_session)
    bakiye = sadakat_deposu.puan_bakiyesi_getir(musteri_id)

Repository Sınıfları:
    MusteriDeposu: Müşteri veritabanı erişim katmanı
        - musteri_olustur(dto) -> Musteriler
        - musteri_guncelle(id, dto) -> Musteriler
        - musteri_getir(id) -> Optional[Musteriler]
        - musteri_ara(dto) -> List[Musteriler]
    
    SadakatDeposu: Sadakat puan veritabanı erişim katmanı
        - puan_kaydi_ekle(dto, islem_turu) -> SadakatPuanlari
        - puan_bakiyesi_getir(musteri_id) -> int
        - puan_hareketleri_listele(musteri_id, limit) -> List[SadakatPuanlari]
"""

# Depolar dosyasından import et
from .crm_depolar import MusteriDeposu, SadakatDeposu

__all__ = ['MusteriDeposu', 'SadakatDeposu']
__version__ = "0.2.0"
__author__ = "SONTECHSP Development Team"
__description__ = "CRM Repository Katmanı - Veri Erişim Yönetimi"