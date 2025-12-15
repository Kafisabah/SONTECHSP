# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar
# Description: SONTECHSP repository pattern sınıfları paketi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Repository Pattern Sınıfları

Bu paket tüm repository (depo) sınıflarını içerir.
Repository pattern ile veritabanı erişimi katmanlı mimari kurallarına uygun şekilde yapılır.

Repository organizasyonu:
- taban.py: TemelDepo abstract base class
- kullanici_depo.py: KullaniciDepo, RolDepo, YetkiDepo
- firma_depo.py: FirmaDepo, MagazaDepo, TerminalDepo
- stok_depo.py: UrunDepo, StokBakiyeDepo, StokHareketDepo
- crm_depo.py: MusteriDepo, SadakatPuanDepo
- pos_depo.py: PosSatisDepo, OdemeKayitDepo
- belge_depo.py: SatisBelgeDepo
- eticaret_depo.py: EticaretHesapDepo, EticaretSiparisDepo
- ebelge_depo.py: EbelgeCikisKuyrukDepo, EbelgeDurumDepo
- kargo_depo.py: KargoEtiketDepo, KargoTakipDepo
"""

from .taban import TemelDepo
from .kullanici_depo import KullaniciDepo, RolDepo, YetkiDepo
from .firma_depo import FirmaDepo, MagazaDepo, TerminalDepo
from .stok_depo import UrunDepo, StokBakiyeDepo, StokHareketDepo
from .crm_depo import MusteriDepo, SadakatPuanDepo
from .pos_depo import PosSatisDepo, OdemeKayitDepo
from .belge_depo import SatisBelgeDepo
from .eticaret_depo import EticaretHesapDepo, EticaretSiparisDepo
from .ebelge_depo import EbelgeCikisKuyrukDepo, EbelgeDurumDepo
from .kargo_depo import KargoEtiketDepo, KargoTakipDepo

__all__ = [
    'TemelDepo',
    'KullaniciDepo', 'RolDepo', 'YetkiDepo',
    'FirmaDepo', 'MagazaDepo', 'TerminalDepo',
    'UrunDepo', 'StokBakiyeDepo', 'StokHareketDepo',
    'MusteriDepo', 'SadakatPuanDepo',
    'PosSatisDepo', 'OdemeKayitDepo',
    'SatisBelgeDepo',
    'EticaretHesapDepo', 'EticaretSiparisDepo',
    'EbelgeCikisKuyrukDepo', 'EbelgeDurumDepo',
    'KargoEtiketDepo', 'KargoTakipDepo'
]