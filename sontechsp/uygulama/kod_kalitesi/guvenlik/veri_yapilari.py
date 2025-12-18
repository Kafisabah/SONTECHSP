# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.veri_yapilari
# Description: Güvenlik sistemi veri yapıları
# Changelog:
# - İlk versiyon: Güvenlik sistemi data class'ları

"""
Güvenlik Sistemi Veri Yapıları

Güvenlik sistemi için kullanılan tüm veri yapılarını içerir.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class IslemTuru(Enum):
    """İşlem türleri"""
    BACKUP_OLUSTUR = "backup_olustur"
    DOSYA_BOL = "dosya_bol"
    FONKSIYON_BOL = "fonksiyon_bol"
    IMPORT_DUZENLE = "import_duzenle"
    BASLIK_EKLE = "baslik_ekle"
    GERI_AL = "geri_al"
    DOGRULA = "dogrula"


class IslemDurumu(Enum):
    """İşlem durumları"""
    BASLADI = "basladi"
    DEVAM_EDIYOR = "devam_ediyor"
    TAMAMLANDI = "tamamlandi"
    HATA = "hata"
    GERI_ALINDI = "geri_alindi"


@dataclass
class IslemKaydi:
    """İşlem kaydı"""
    islem_id: str
    islem_turu: IslemTuru
    durum: IslemDurumu
    baslangic_zamani: datetime
    bitis_zamani: Optional[datetime] = None
    hedef_dosyalar: List[str] = field(default_factory=list)
    degisiklikler: Dict[str, Any] = field(default_factory=dict)
    hata_mesaji: Optional[str] = None
    kullanici: str = "sistem"
    backup_yolu: Optional[str] = None


@dataclass
class BackupBilgisi:
    """Backup bilgisi"""
    backup_id: str
    olusturma_zamani: datetime
    proje_yolu: str
    backup_yolu: str
    dosya_sayisi: int
    toplam_boyut: int
    hash_degeri: str
    aciklama: str = ""