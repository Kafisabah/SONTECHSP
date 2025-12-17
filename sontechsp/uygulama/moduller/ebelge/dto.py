# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge.dto
# Description: E-belge modülü veri transfer nesneleri
# Changelog:
# - İlk versiyon: DTO sınıfları oluşturuldu

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional


@dataclass
class EBelgeOlusturDTO:
    """E-belge oluşturma isteği için veri transfer nesnesi"""
    kaynak_turu: str          # POS_SATIS, SATIS_BELGESI, IADE_BELGESI
    kaynak_id: int            # Kaynak sistemdeki belge ID'si
    belge_turu: str           # EFATURA, EARSIV, EIRSALIYE
    musteri_ad: str           # Müşteri adı
    vergi_no: str             # Müşteri vergi/TC numarası
    toplam_tutar: Decimal     # Belge toplam tutarı
    belge_json: Dict          # Belge detay verileri
    para_birimi: str = "TRY"  # Para birimi
    aciklama: Optional[str] = None  # İsteğe bağlı açıklama


@dataclass
class EBelgeGonderDTO:
    """Entegratöre belge gönderimi için veri transfer nesnesi"""
    cikis_id: int            # Kuyruk kaydı ID'si
    belge_json: Dict         # Entegratöre gönderilecek JSON verisi


@dataclass
class EBelgeSonucDTO:
    """Entegratörden gelen sonuç için veri transfer nesnesi"""
    basarili_mi: bool                      # İşlem başarı durumu
    dis_belge_no: Optional[str] = None     # Entegratörden alınan belge numarası
    durum_kodu: Optional[str] = None       # Entegratör durum kodu
    mesaj: Optional[str] = None            # Hata/başarı mesajı
    ham_cevap_json: Optional[Dict] = None  # Entegratörden gelen ham cevap


@dataclass
class EBelgeDurumSorguDTO:
    """Belge durum sorgulama için veri transfer nesnesi"""
    cikis_id: int                      # Kuyruk kaydı ID'si
    dis_belge_no: Optional[str] = None # Dış belge numarası