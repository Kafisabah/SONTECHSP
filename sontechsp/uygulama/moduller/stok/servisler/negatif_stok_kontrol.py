# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.negatif_stok_kontrol
# Description: Negatif stok kontrol servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Negatif Stok Kontrol Servisi

Bu modül negatif stok kontrol kurallarını uygular.
Stok seviyesi kuralları: 0: uyarı, -1 ile -5: uyarı+izin, <-5: engel
"""

from decimal import Decimal
from typing import Optional, Dict
from enum import Enum

from ..hatalar import NegatifStokError
from .arayuzler import INegatifStokKontrol


class StokKontrolSonucu(Enum):
    """Stok kontrol sonuç tipleri"""
    IZIN_VER = "IZIN_VER"
    UYARI_VER = "UYARI_VER"
    ENGELLE = "ENGELLE"


class NegatifStokKontrol(INegatifStokKontrol):
    """Negatif stok kontrol servisi"""
    
    def __init__(self):
        # Varsayılan limitler
        self.varsayilan_limit = Decimal('-5.0000')
        self.uyari_baslangic = Decimal('0.0000')
        
        # Ürün bazlı özel limitler
        self.urun_limitleri: Dict[int, Decimal] = {}
    
    def kontrol_yap(self, urun_id: int, talep_miktar: Decimal, 
                   mevcut_stok: Decimal) -> bool:
        """
        Negatif stok kontrolü yapar
        
        Returns:
            True: İşleme izin ver
            False: İşlemi engelle
            
        Raises:
            NegatifStokError: Engelleme durumunda
        """
        # Yeni stok seviyesini hesapla
        yeni_stok = mevcut_stok - talep_miktar
        
        # Kontrol sonucunu belirle
        sonuc = self._stok_seviyesi_kontrol(urun_id, yeni_stok, mevcut_stok, talep_miktar)
        
        if sonuc == StokKontrolSonucu.IZIN_VER:
            return True
        elif sonuc == StokKontrolSonucu.UYARI_VER:
            # Uyarı ver ama işleme izin ver
            return True
        else:  # ENGELLE
            # Hata fırlat
            limit = self._urun_limiti_getir(urun_id)
            raise NegatifStokError(
                f"Negatif stok limiti aşıldı. Limit: {limit}, Yeni stok: {yeni_stok}",
                f"urun_id:{urun_id}",
                mevcut_stok,
                talep_miktar,
                limit
            )
    
    def limit_belirle(self, urun_id: int, limit: Decimal) -> None:
        """Ürün bazlı negatif stok limiti belirler"""
        if limit > 0:
            raise ValueError("Negatif stok limiti pozitif olamaz")
        
        self.urun_limitleri[urun_id] = limit
    
    def limit_kaldir(self, urun_id: int) -> None:
        """Ürün bazlı limiti kaldırır (varsayılana döner)"""
        if urun_id in self.urun_limitleri:
            del self.urun_limitleri[urun_id]
    
    def urun_limiti_getir(self, urun_id: int) -> Decimal:
        """Ürünün negatif stok limitini getirir"""
        return self._urun_limiti_getir(urun_id)
    
    def _stok_seviyesi_kontrol(self, urun_id: int, yeni_stok: Decimal, 
                             mevcut_stok: Decimal, talep_miktar: Decimal) -> StokKontrolSonucu:
        """Stok seviyesi kontrolü yapar"""
        limit = self._urun_limiti_getir(urun_id)
        
        # Pozitif stok - izin ver
        if yeni_stok >= self.uyari_baslangic:
            return StokKontrolSonucu.IZIN_VER
        
        # Sıfır stok - uyarı ver
        if yeni_stok == Decimal('0.0000'):
            return StokKontrolSonucu.UYARI_VER
        
        # -1 ile -5 arası - uyarı ver ama izin ver
        if yeni_stok >= Decimal('-5.0000') and yeni_stok >= limit:
            return StokKontrolSonucu.UYARI_VER
        
        # Limit altı - engelle
        if yeni_stok < limit:
            return StokKontrolSonucu.ENGELLE
        
        # Varsayılan - uyarı ver
        return StokKontrolSonucu.UYARI_VER
    
    def _urun_limiti_getir(self, urun_id: int) -> Decimal:
        """Ürün için geçerli limiti getirir"""
        return self.urun_limitleri.get(urun_id, self.varsayilan_limit)
    
    def kontrol_durumu_getir(self, urun_id: int, mevcut_stok: Decimal) -> Dict:
        """Mevcut stok durumu bilgisi getirir"""
        limit = self._urun_limiti_getir(urun_id)
        
        durum = {
            'mevcut_stok': mevcut_stok,
            'limit': limit,
            'durum': 'NORMAL'
        }
        
        if mevcut_stok <= Decimal('0.0000'):
            if mevcut_stok >= limit:
                durum['durum'] = 'UYARI'
            else:
                durum['durum'] = 'KRITIK'
        
        return durum