# Version: 0.2.0
# Last Update: 2024-12-17
# Module: crm.servisler
# Description: CRM modülü servis katmanı
# Changelog:
# - İlk oluşturma
# - v0.2.0: Public API export'u tamamlandı, dokümantasyon güncellendi

"""
SONTECHSP CRM Servis Katmanı

Bu katman CRM modülünün iş mantığını içerir:
- Müşteri servisleri (MusteriServisi)
- Sadakat puanı servisleri (SadakatServisi)

Katman kuralları:
- UI katmanından çağrılır
- Repository katmanını kullanır
- İş kurallarını uygular
- Müşteri iş süreçlerini yönetir
- Transaction yönetimi sağlar
- Validation ve hata yönetimi yapar

Kullanım Örneği:
    from sontechsp.uygulama.moduller.crm.servisler import MusteriServisi, SadakatServisi
    
    # Müşteri servisi kullanımı
    musteri_servisi = MusteriServisi(db_session)
    musteri = musteri_servisi.musteri_olustur(dto)
    
    # Sadakat servisi kullanımı
    sadakat_servisi = SadakatServisi(db_session)
    bakiye = sadakat_servisi.bakiye_getir(musteri_id)

Servis Sınıfları:
    MusteriServisi: Müşteri CRUD işlemleri ve arama
        - musteri_olustur(dto) -> Musteriler
        - musteri_guncelle(id, dto) -> Musteriler
        - musteri_getir(id) -> Optional[Musteriler]
        - musteri_ara(dto) -> List[Musteriler]
    
    SadakatServisi: Puan kazanım, harcama ve bakiye yönetimi
        - puan_kazan(dto) -> SadakatPuanlari
        - puan_harca(dto) -> SadakatPuanlari
        - bakiye_getir(musteri_id) -> int
        - hareketler(musteri_id, limit) -> List[SadakatPuanlari]
        - puan_duzelt(dto) -> SadakatPuanlari
"""

# Servisler dosyasından import et
from .crm_servisler import MusteriServisi, SadakatServisi

__all__ = ['MusteriServisi', 'SadakatServisi']
__version__ = "0.2.0"
__author__ = "SONTECHSP Development Team"
__description__ = "CRM Servis Katmanı - İş Mantığı Yönetimi"