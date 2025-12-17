# Version: 0.2.0
# Last Update: 2024-12-17
# Module: crm
# Description: Müşteri ilişkileri modülü (crm_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi
# - CRM çekirdek bileşenleri eklendi: DTO, sabitler, servisler, depolar, entegrasyon
# - v0.2.0: Tüm public API'ler export edildi, modül dokümantasyonu güncellendi

"""
SONTECHSP CRM Modülü

Bu modül müşteri ilişkileri yönetimini içerir:
- Müşteri yönetimi (CRUD işlemleri)
- Sadakat puanı sistemi (kazanım, harcama, düzeltme)
- POS ve satış belgeleri entegrasyonu

Katmanlı yapı:
- servisler/: İş mantığı katmanı (MusteriServisi, SadakatServisi)
- depolar/: Repository katmanı (MusteriDeposu, SadakatDeposu)
- dto.py: Veri transfer objeleri
- sabitler.py: Enum ve sabit değerler
- entegrasyon_kancalari.py: Diğer modüllerle entegrasyon

Kullanım Örneği:
    from sontechsp.uygulama.moduller.crm import (
        MusteriServisi, SadakatServisi,
        MusteriOlusturDTO, PuanIslemDTO,
        PuanIslemTuru, ReferansTuru
    )
    
    # Müşteri oluşturma
    dto = MusteriOlusturDTO(ad="Ahmet", soyad="Yılmaz")
    musteri_servisi = MusteriServisi(db)
    musteri = musteri_servisi.musteri_olustur(dto)
    
    # Puan kazanımı
    puan_dto = PuanIslemDTO(musteri_id=musteri.id, puan=100)
    sadakat_servisi = SadakatServisi(db)
    sadakat_servisi.puan_kazan(puan_dto)

Gereksinimler:
    - Requirements 12.1: Modül bağımsızlığı sağlanmıştır
    - Requirements 12.2: Temiz API export'u yapılmıştır
"""

# Temel bileşenleri import et
from .dto import (
    MusteriOlusturDTO,
    MusteriGuncelleDTO, 
    PuanIslemDTO,
    MusteriAraDTO
)
from .sabitler import (
    PuanIslemTuru, 
    ReferansTuru,
    VARSAYILAN_PUAN_HAREKET_LIMIT,
    PUAN_HESAPLAMA_ORANI
)

# Servis katmanından import et
from .servisler import MusteriServisi, SadakatServisi

# Repository katmanından import et  
from .depolar import MusteriDeposu, SadakatDeposu

# Entegrasyon hook'larını import et
from .entegrasyon_kancalari import pos_satis_tamamlandi, satis_belgesi_olustu

# Alt modülleri import et
from . import servisler
from . import depolar

__version__ = "0.2.0"
__author__ = "SONTECHSP Development Team"
__email__ = "dev@sontechsp.com"
__description__ = "CRM Çekirdek Modülü - Müşteri İlişkileri Yönetimi"

__all__ = [
    # DTO sınıfları
    "MusteriOlusturDTO",
    "MusteriGuncelleDTO", 
    "PuanIslemDTO",
    "MusteriAraDTO",
    
    # Enum'lar ve sabitler
    "PuanIslemTuru",
    "ReferansTuru", 
    "VARSAYILAN_PUAN_HAREKET_LIMIT",
    "PUAN_HESAPLAMA_ORANI",
    
    # Servis sınıfları
    "MusteriServisi",
    "SadakatServisi",
    
    # Repository sınıfları
    "MusteriDeposu", 
    "SadakatDeposu",
    
    # Entegrasyon fonksiyonları
    "pos_satis_tamamlandi",
    "satis_belgesi_olustu",
    
    # Alt modüller
    "servisler",
    "depolar"
]