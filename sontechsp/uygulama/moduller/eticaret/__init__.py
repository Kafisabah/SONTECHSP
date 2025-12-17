# Version: 0.2.0
# Last Update: 2024-12-17
# Module: eticaret
# Description: E-ticaret entegrasyonu modülü - Genel API yüzeyi
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi
# - Genel API yüzeyi tanımlandı (v0.2.0)

"""
SONTECHSP E-ticaret Entegrasyon Modülü

Bu modül e-ticaret entegrasyonlarını yönetir:
- Pazaryeri entegrasyonları (Trendyol, Shopify, Amazon vb.)
- E-ticaret sitesi bağlantıları
- Sipariş senkronizasyonu
- Stok ve fiyat güncellemeleri
- Asenkron iş kuyruğu sistemi

Mimari:
- Service-Repository pattern
- Platform bağımsız soyutlama katmanı
- Asenkron job queue sistemi
- Kapsamlı hata yönetimi

Katmanlı yapı:
- servisler/: İş mantığı katmanı
- depolar/: Repository katmanı  
- modeller/: Veri modelleri katmanı
- Entegrasyon katmanı: BaglantiArayuzu, BaglantiFabrikasi
"""

# Ana servis sınıfları
from .servisler.eticaret_servisi import EticaretServisi
from .job_kosucu import JobKosucu

# Veri transfer nesneleri (DTOs)
from .dto import (
    MagazaHesabiOlusturDTO,
    MagazaHesabiGuncelleDTO,
    SiparisDTO,
    StokGuncelleDTO,
    FiyatGuncelleDTO,
    JobDTO,
    JobSonucDTO
)

# Sabitler ve enum'lar
from .sabitler import (
    Platformlar,
    SiparisDurumlari,
    JobTurleri,
    JobDurumlari,
    VARSAYILAN_PARA_BIRIMI,
    MAKSIMUM_YENIDEN_DENEME,
    YENIDEN_DENEME_ARALIĞI_DAKIKA
)

# Hata sınıfları
from .hatalar import (
    EntegrasyonHatasi,
    BaglantiHatasi,
    VeriDogrulamaHatasi,
    PlatformHatasi,
    JobHatasi
)

# Entegrasyon arayüzü ve fabrika
from .baglanti_arayuzu import BaglantiArayuzu
from .baglanti_fabrikasi import BaglantiFabrikasi

# Depo sınıfları (repository pattern)
from .depolar.eticaret_deposu import EticaretDeposu
from .depolar.job_deposu import JobDeposu

# Yardımcı modüller
from .sifreleme import KimlikSifreleme
from .dogrulama import (
    siparis_durum_gecisini_dogrula,
    stok_guncellemelerini_dogrula,
    fiyat_guncellemelerini_dogrula
)
from .monitoring import MonitoringServisi

# Alt modülleri import et (geriye uyumluluk için)
from . import servisler
from . import depolar
from . import modeller

__version__ = "0.2.0"

# Genel API yüzeyi - dışarıya açılan ana bileşenler
__all__ = [
    # Ana servis sınıfları
    "EticaretServisi",
    "JobKosucu",
    
    # Veri transfer nesneleri
    "MagazaHesabiOlusturDTO",
    "MagazaHesabiGuncelleDTO", 
    "SiparisDTO",
    "StokGuncelleDTO",
    "FiyatGuncelleDTO",
    "JobDTO",
    "JobSonucDTO",
    
    # Sabitler ve enum'lar
    "Platformlar",
    "SiparisDurumlari",
    "JobTurleri",
    "JobDurumlari",
    "VARSAYILAN_PARA_BIRIMI",
    "MAKSIMUM_YENIDEN_DENEME",
    "YENIDEN_DENEME_ARALIĞI_DAKIKA",
    
    # Hata sınıfları
    "EntegrasyonHatasi",
    "BaglantiHatasi",
    "VeriDogrulamaHatasi",
    "PlatformHatasi",
    "JobHatasi",
    
    # Entegrasyon arayüzü
    "BaglantiArayuzu",
    "BaglantiFabrikasi",
    
    # Depo sınıfları
    "EticaretDeposu",
    "JobDeposu",
    
    # Yardımcı sınıflar
    "KimlikSifreleme",
    "MonitoringServisi",
    
    # Doğrulama fonksiyonları
    "siparis_durum_gecisini_dogrula",
    "stok_guncellemelerini_dogrula", 
    "fiyat_guncellemelerini_dogrula",
    
    # Alt modüller (geriye uyumluluk)
    "servisler",
    "depolar", 
    "modeller"
]

# Modül düzeyinde dokümantasyon
def get_version():
    """Modül versiyonunu döndürür"""
    return __version__

def get_supported_platforms():
    """Desteklenen platformları döndürür"""
    return [platform.value for platform in Platformlar]

def get_order_statuses():
    """Desteklenen sipariş durumlarını döndürür"""
    return [durum.value for durum in SiparisDurumlari]

def get_job_types():
    """Desteklenen iş türlerini döndürür"""
    return [tur.value for tur in JobTurleri]

# Temiz import yapısı için kısa yollar
create_store_account = lambda *args, **kwargs: EticaretServisi(*args, **kwargs).magaza_hesabi_olustur
update_store_account = lambda *args, **kwargs: EticaretServisi(*args, **kwargs).magaza_hesabi_guncelle
sync_orders = lambda *args, **kwargs: EticaretServisi(*args, **kwargs).siparis_senkronize_et
update_order_status = lambda *args, **kwargs: EticaretServisi(*args, **kwargs).siparis_durum_guncelle