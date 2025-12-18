# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.orkestrator.veri_yapilari
# Description: Refactoring orkestratörü veri yapıları
# Changelog:
# - İlk versiyon: Refactoring veri yapıları

"""
Refactoring Orkestratörü Veri Yapıları

Refactoring sürecinde kullanılan tüm veri yapılarını içerir.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class RefactoringAsamasi(Enum):
    """Refactoring aşamaları"""
    ANALIZ = "analiz"
    PLANLAMA = "planlama"
    BACKUP = "backup"
    UYGULAMA = "uygulama"
    DOGRULAMA = "dogrulama"
    TAMAMLANDI = "tamamlandi"
    HATA = "hata"


class RefactoringSonucu(Enum):
    """Refactoring sonuçları"""
    BASARILI = "basarili"
    BASARISIZ = "basarisiz"
    KISMI_BASARILI = "kismi_basarili"
    IPTAL_EDILDI = "iptal_edildi"


@dataclass
class RefactoringAdimi:
    """Refactoring adımı bilgisi"""
    adim_id: str
    aciklama: str
    hedef_dosyalar: List[str]
    durum: str = "bekliyor"
    hata_mesaji: Optional[str] = None
    baslangic_zamani: Optional[datetime] = None
    bitis_zamani: Optional[datetime] = None


@dataclass
class RefactoringPlani:
    """Refactoring planı"""
    plan_id: str
    proje_yolu: str
    hedef_klasorler: List[str]
    adimlar: List[RefactoringAdimi] = field(default_factory=list)
    toplam_dosya_sayisi: int = 0
    sorunlu_dosya_sayisi: int = 0
    tahmini_sure: int = 0  # dakika cinsinden


@dataclass
class RefactoringRaporu:
    """Refactoring raporu"""
    plan_id: str
    baslangic_zamani: datetime
    bitis_zamani: Optional[datetime] = None
    durum: RefactoringSonucu = RefactoringSonucu.BASARISIZ
    islenen_dosya_sayisi: int = 0
    basarili_adim_sayisi: int = 0
    basarisiz_adim_sayisi: int = 0
    hata_mesajlari: List[str] = field(default_factory=list)
    backup_yolu: Optional[str] = None