# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge.saglayici_fabrikasi
# Description: E-belge sağlayıcı fabrikası
# Changelog:
# - İlk versiyon: SaglayiciFabrikasi ve DummySaglayici oluşturuldu

import logging
import random
from typing import Optional, Dict, Any

from .saglayici_arayuzu import SaglayiciArayuzu
from .dto import EBelgeGonderDTO, EBelgeSonucDTO
from .hatalar import KonfigurasyonHatasi, BaglantiHatasi

logger = logging.getLogger(__name__)


class DummySaglayici(SaglayiciArayuzu):
    """Test ve geliştirme için dummy sağlayıcı"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.simulasyon_modu = self.config.get('simulasyon_modu', True)
        self.her_zaman_basarili = self.config.get('her_zaman_basarili', False)
        self.log_seviyesi = self.config.get('log_seviyesi', 'INFO')
        
    def gonder(self, dto: EBelgeGonderDTO) -> EBelgeSonucDTO:
        """Dummy belge gönderimi"""
        logger.info(f"DummySaglayici: Belge gönderiliyor - Çıkış ID: {dto.cikis_id}")
        
        if self.her_zaman_basarili:
            return EBelgeSonucDTO(
                basarili_mi=True,
                dis_belge_no=f"DUMMY-{dto.cikis_id}-{random.randint(1000, 9999)}",
                durum_kodu="200",
                mesaj="Başarılı (Dummy)",
                ham_cevap_json={"status": "success", "dummy": True}
            )
        
        if self.simulasyon_modu:
            # %80 başarı oranı
            basarili = random.random() < 0.8
            if basarili:
                return EBelgeSonucDTO(
                    basarili_mi=True,
                    dis_belge_no=f"DUMMY-{dto.cikis_id}-{random.randint(1000, 9999)}",
                    durum_kodu="200",
                    mesaj="Başarılı (Simülasyon)",
                    ham_cevap_json={"status": "success", "simulation": True}
                )
            else:
                return EBelgeSonucDTO(
                    basarili_mi=False,
                    durum_kodu="500",
                    mesaj="Simülasyon hatası",
                    ham_cevap_json={"status": "error", "simulation": True}
                )
        
        # Varsayılan başarılı sonuç
        return EBelgeSonucDTO(
            basarili_mi=True,
            dis_belge_no=f"DUMMY-{dto.cikis_id}",
            durum_kodu="200",
            mesaj="Başarılı (Varsayılan)",
            ham_cevap_json={"status": "success", "default": True}
        )
    
    def durum_sorgula(self, dis_belge_no: str) -> EBelgeSonucDTO:
        """Dummy durum sorgulama"""
        logger.info(f"DummySaglayici: Durum sorgulanıyor - Belge No: {dis_belge_no}")
        
        return EBelgeSonucDTO(
            basarili_mi=True,
            dis_belge_no=dis_belge_no,
            durum_kodu="GONDERILDI",
            mesaj="Belge başarıyla gönderildi (Dummy)",
            ham_cevap_json={"status": "delivered", "dummy": True}
        )


class SaglayiciFabrikasi:
    """Sağlayıcı fabrikası"""
    
    _saglayicilar: Dict[str, type] = {
        'dummy': DummySaglayici,
    }
    
    @classmethod
    def saglayici_olustur(
        cls, 
        saglayici_adi: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> SaglayiciArayuzu:
        """Konfigürasyona göre sağlayıcı oluşturur"""
        
        if not saglayici_adi:
            logger.warning("Sağlayıcı adı belirtilmedi, DummySaglayici kullanılıyor")
            return DummySaglayici(config)
        
        saglayici_sinifi = cls._saglayicilar.get(saglayici_adi.lower())
        
        if not saglayici_sinifi:
            logger.warning(f"Sağlayıcı bulunamadı: {saglayici_adi}, DummySaglayici kullanılıyor")
            return DummySaglayici(config)
        
        try:
            return saglayici_sinifi(config)
        except Exception as e:
            raise KonfigurasyonHatasi(f"Sağlayıcı oluşturulamadı: {saglayici_adi} - {str(e)}")
    
    @classmethod
    def saglayici_ekle(cls, ad: str, saglayici_sinifi: type):
        """Yeni sağlayıcı ekler"""
        if not issubclass(saglayici_sinifi, SaglayiciArayuzu):
            raise KonfigurasyonHatasi(
                f"Sağlayıcı SaglayiciArayuzu'nden türetilmelidir: {saglayici_sinifi}"
            )
        
        cls._saglayicilar[ad.lower()] = saglayici_sinifi
        logger.info(f"Yeni sağlayıcı eklendi: {ad}")
    
    @classmethod
    def mevcut_saglayicilar(cls) -> list:
        """Mevcut sağlayıcıları listeler"""
        return list(cls._saglayicilar.keys())