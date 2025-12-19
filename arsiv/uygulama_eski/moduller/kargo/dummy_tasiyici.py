# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo.dummy_tasiyici
# Description: Test amaçlı dummy taşıyıcı implementasyonu
# Changelog:
# - DummyTasiyici class'ı eklendi
# - Sahte takip numarası üretimi eklendi
# - Test amaçlı sahte durum döndürme eklendi

"""
Test amaçlı dummy taşıyıcı implementasyonu.

Bu modül, gerçek kargo API'si olmadan test edilebilir
sahte taşıyıcı implementasyonu sağlar.
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any

from .tasiyici_arayuzu import TasiyiciArayuzu
from .sabitler import EtiketDurumlari, TakipDurumlari


class DummyTasiyici(TasiyiciArayuzu):
    """
    Test amaçlı dummy taşıyıcı implementasyonu.
    
    Gerçek API çağrıları yapmadan sahte veriler döndürür.
    Geliştirme ve test aşamalarında kullanılır.
    """
    
    def __init__(self, basari_orani: float = 0.9):
        """
        Dummy taşıyıcı oluşturur.
        
        Args:
            basari_orani: Etiket oluşturma başarı oranı (0.0-1.0)
        """
        self.basari_orani = basari_orani
    
    def etiket_olustur(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sahte etiket oluşturur.
        
        Args:
            payload: Etiket oluşturma verileri
        
        Returns:
            Dict[str, Any]: Sahte etiket oluşturma sonucu
        """
        # Rastgele başarı/başarısızlık simülasyonu
        if random.random() < self.basari_orani:
            # Başarılı durum
            takip_no = self._sahte_takip_no_uret()
            return {
                'takip_no': takip_no,
                'etiket_verisi_base64': None,  # MVP'de etiket verisi yok
                'durum': EtiketDurumlari.OLUSTURULDU,
                'mesaj': f'Etiket başarıyla oluşturuldu. Takip No: {takip_no}'
            }
        else:
            # Hata durumu
            hata_mesajlari = [
                'Geçersiz adres bilgisi',
                'Taşıyıcı servisi geçici olarak kullanılamıyor',
                'Paket ağırlığı limiti aşıldı',
                'Alıcı telefon numarası geçersiz'
            ]
            return {
                'takip_no': None,
                'etiket_verisi_base64': None,
                'durum': EtiketDurumlari.HATA,
                'mesaj': random.choice(hata_mesajlari)
            }
    
    def durum_sorgula(self, takip_no: str) -> Dict[str, Any]:
        """
        Sahte durum sorgular.
        
        Args:
            takip_no: Takip numarası
        
        Returns:
            Dict[str, Any]: Sahte durum bilgisi
        """
        # Takip numarası formatını kontrol et
        if not takip_no or len(takip_no) < 10:
            return {
                'durum': TakipDurumlari.BILINMIYOR,
                'aciklama': 'Geçersiz takip numarası',
                'zaman': datetime.now()
            }
        
        # Rastgele durum seç
        durumlar = [
            (TakipDurumlari.KARGODA, 'Kargo dağıtım merkezinde'),
            (TakipDurumlari.KARGODA, 'Kargo yolda'),
            (TakipDurumlari.TESLIM, 'Kargo teslim edildi'),
            (TakipDurumlari.IPTAL, 'Kargo iptal edildi')
        ]
        
        durum, aciklama = random.choice(durumlar)
        
        # Rastgele zaman (son 7 gün içinde)
        zaman = datetime.now() - timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        return {
            'durum': durum,
            'aciklama': aciklama,
            'zaman': zaman
        }
    
    def _sahte_takip_no_uret(self) -> str:
        """
        Sahte takip numarası üretir.
        
        Returns:
            str: Sahte takip numarası
        """
        # UUID'nin son 12 karakterini kullan
        return str(uuid.uuid4()).replace('-', '').upper()[:12]
    
    def get_tasiyici_adi(self) -> str:
        """Taşıyıcı adını döndürür."""
        return "DUMMY_TASIYICI"