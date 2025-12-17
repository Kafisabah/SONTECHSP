# Version: 0.1.0
# Last Update: 2024-12-17
# Module: satis_belgeleri.servisler.sorgu_servisi
# Description: Belge sorgu servisi
# Changelog:
# - 0.1.0: İlk sürüm - Belge sorgu işlemleri

"""
Belge Sorgu Servisi

Bu modül belge sorgu işlemlerini yönetir.
"""

from typing import List, Optional
from datetime import datetime

from ..dto.belge_dto import BelgeDTO
from ..dto.belge_ozet_dto import BelgeOzetDTO
from ..dto.filtre_dto import BelgeFiltresiDTO, SayfalamaDTO, SayfaliSonucDTO
from ..depolar.belge_deposu import IBelgeDeposu
from ....cekirdek.hatalar import IsKuraliHatasi, VeriTabaniHatasi


class SorguServisi:
    """Belge sorgu servisi"""
    
    def __init__(self, belge_deposu: IBelgeDeposu):
        """
        Sorgu servisi başlatıcı
        
        Args:
            belge_deposu: Belge repository
        """
        self._belge_deposu = belge_deposu
    
    def belge_listesi(self, filtre: BelgeFiltresiDTO, sayfalama: SayfalamaDTO) -> SayfaliSonucDTO[BelgeOzetDTO]:
        """
        Belge listesi getir
        
        Args:
            filtre: Filtreleme kriterleri
            sayfalama: Sayfalama parametreleri
            
        Returns:
            Sayfalı belge listesi
            
        Raises:
            VeriTabaniHatasi: Veritabanı hatası durumunda
        """
        try:
            # Toplam kayıt sayısını al
            toplam_kayit = self._belge_deposu.toplam_sayisi(filtre)
            
            # Belgeleri getir
            belgeler = self._belge_deposu.sayfalanmis_listele(filtre, sayfalama)
            
            # DTO'ya dönüştür
            belge_ozet_listesi = [BelgeOzetDTO.from_model(belge) for belge in belgeler]
            
            return SayfaliSonucDTO(
                veriler=belge_ozet_listesi,
                toplam_kayit=toplam_kayit,
                sayfa=sayfalama.sayfa,
                sayfa_boyutu=sayfalama.sayfa_boyutu
            )
            
        except Exception as e:
            raise VeriTabaniHatasi(f"Belge listesi alınamadı: {e}")
    
    def belge_detay(self, belge_id: int) -> Optional[BelgeDTO]:
        """
        Belge detayını getir
        
        Args:
            belge_id: Belge ID
            
        Returns:
            Belge detayı veya None
            
        Raises:
            VeriTabaniHatasi: Veritabanı hatası durumunda
        """
        try:
            belge = self._belge_deposu.bul(belge_id)
            if belge:
                return BelgeDTO.from_model(belge)
            return None
            
        except Exception as e:
            raise VeriTabaniHatasi(f"Belge detayı alınamadı: {e}")
    
    def belge_gecmisi(self, belge_id: int) -> List[dict]:
        """
        Belge durum geçmişini getir
        
        Args:
            belge_id: Belge ID
            
        Returns:
            Durum geçmiş listesi
            
        Raises:
            VeriTabaniHatasi: Veritabanı hatası durumunda
        """
        try:
            gecmis = self._belge_deposu.durum_gecmisi(belge_id)
            return [
                {
                    'id': g.id,
                    'eski_durum': g.eski_durum.value if g.eski_durum else None,
                    'yeni_durum': g.yeni_durum.value,
                    'degisiklik_tarihi': g.degisiklik_tarihi.isoformat(),
                    'degistiren_kullanici_id': g.degistiren_kullanici_id,
                    'aciklama': g.aciklama
                }
                for g in gecmis
            ]
            
        except Exception as e:
            raise VeriTabaniHatasi(f"Belge geçmişi alınamadı: {e}")
    
    def durum_bazli_belgeler(self, durum: str, sayfalama: SayfalamaDTO) -> SayfaliSonucDTO[BelgeOzetDTO]:
        """
        Duruma göre belgeleri getir
        
        Args:
            durum: Belge durumu
            sayfalama: Sayfalama parametreleri
            
        Returns:
            Sayfalı belge listesi
            
        Raises:
            VeriTabaniHatasi: Veritabanı hatası durumunda
        """
        try:
            from ..modeller import BelgeDurumu
            
            # Durum enum'a çevir
            belge_durumu = BelgeDurumu(durum)
            
            # Filtre oluştur
            filtre = BelgeFiltresiDTO(belge_durumu=belge_durumu)
            
            return self.belge_listesi(filtre, sayfalama)
            
        except ValueError:
            raise IsKuraliHatasi(f"Geçersiz belge durumu: {durum}")
        except Exception as e:
            raise VeriTabaniHatasi(f"Durum bazlı belgeler alınamadı: {e}")