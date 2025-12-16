# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.stok_sayim_service
# Description: SONTECHSP stok sayım servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Sayım Servisi

Bu modül stok sayım işlemlerini yöneten servis sınıfını içerir.
Sayım başlatma, tamamlama ve iptal işlemlerini gerçekleştirir.
"""

from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum

from ..dto import StokHareketDTO, StokBakiyeDTO
from ..depolar.arayuzler import IStokHareketRepository, IStokBakiyeRepository
from ..hatalar.stok_hatalari import StokValidationError, StokSayimError


class SayimDurumu(Enum):
    """Sayım durumları"""
    BASLADI = "BASLADI"
    DEVAM_EDIYOR = "DEVAM_EDIYOR"
    TAMAMLANDI = "TAMAMLANDI"
    IPTAL_EDILDI = "IPTAL_EDILDI"


class StokSayimService:
    """Stok sayım servisi implementasyonu"""
    
    def __init__(self, 
                 hareket_repository: IStokHareketRepository,
                 bakiye_repository: IStokBakiyeRepository):
        """
        Stok sayım servisi constructor
        
        Args:
            hareket_repository: Stok hareket repository
            bakiye_repository: Stok bakiye repository
        """
        self._hareket_repository = hareket_repository
        self._bakiye_repository = bakiye_repository
        self._aktif_sayimlar: Dict[str, Dict] = {}  # sayim_id -> sayim_bilgileri
    
    def sayim_baslat(self, 
                    magaza_id: int, 
                    depo_id: Optional[int] = None,
                    kullanici_id: Optional[int] = None,
                    aciklama: Optional[str] = None) -> str:
        """
        Stok sayım işlemini başlatır
        
        Args:
            magaza_id: Mağaza ID
            depo_id: Depo ID (opsiyonel)
            kullanici_id: Sayımı başlatan kullanıcı ID
            aciklama: Sayım açıklaması
            
        Returns:
            str: Sayım ID
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if magaza_id <= 0:
            raise StokValidationError("Geçerli mağaza ID gereklidir")
        
        # Sayım ID oluştur
        sayim_id = f"SAYIM_{magaza_id}_{depo_id or 0}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Sayım bilgilerini kaydet
        sayim_bilgileri = {
            'sayim_id': sayim_id,
            'magaza_id': magaza_id,
            'depo_id': depo_id,
            'kullanici_id': kullanici_id,
            'aciklama': aciklama,
            'durum': SayimDurumu.BASLADI,
            'baslangic_tarihi': datetime.utcnow(),
            'sayim_verileri': {},  # urun_id -> sayilan_miktar
            'sistem_bakiyeleri': {}  # urun_id -> sistem_miktar
        }
        
        # Mevcut sistem bakiyelerini al
        mevcut_bakiyeler = self._bakiye_repository.magaza_bakiyeleri_getir(magaza_id, depo_id)
        
        for bakiye in mevcut_bakiyeler:
            sayim_bilgileri['sistem_bakiyeleri'][bakiye.urun_id] = bakiye.miktar
        
        self._aktif_sayimlar[sayim_id] = sayim_bilgileri
        
        return sayim_id
    
    def sayim_veri_ekle(self, 
                       sayim_id: str, 
                       urun_id: int, 
                       sayilan_miktar: Decimal) -> None:
        """
        Sayım verisi ekler
        
        Args:
            sayim_id: Sayım ID
            urun_id: Ürün ID
            sayilan_miktar: Sayılan miktar
            
        Raises:
            StokSayimError: Sayım hatası durumunda
        """
        if sayim_id not in self._aktif_sayimlar:
            raise StokSayimError(f"Aktif sayım bulunamadı: {sayim_id}")
        
        sayim = self._aktif_sayimlar[sayim_id]
        
        if sayim['durum'] not in [SayimDurumu.BASLADI, SayimDurumu.DEVAM_EDIYOR]:
            raise StokSayimError(f"Sayım durumu veri eklemeye uygun değil: {sayim['durum']}")
        
        if urun_id <= 0:
            raise StokValidationError("Geçerli ürün ID gereklidir")
        
        if sayilan_miktar < 0:
            raise StokValidationError("Sayılan miktar negatif olamaz")
        
        # Sayım verisini ekle
        sayim['sayim_verileri'][urun_id] = sayilan_miktar
        sayim['durum'] = SayimDurumu.DEVAM_EDIYOR
    
    def sayim_tamamla(self, sayim_id: str) -> Dict[int, Decimal]:
        """
        Sayım işlemini tamamlar ve farkları hesaplar
        
        Args:
            sayim_id: Sayım ID
            
        Returns:
            Dict[int, Decimal]: Ürün ID -> Fark miktarı mapping
            
        Raises:
            StokSayimError: Sayım hatası durumunda
        """
        if sayim_id not in self._aktif_sayimlar:
            raise StokSayimError(f"Aktif sayım bulunamadı: {sayim_id}")
        
        sayim = self._aktif_sayimlar[sayim_id]
        
        if sayim['durum'] == SayimDurumu.TAMAMLANDI:
            raise StokSayimError("Sayım zaten tamamlanmış")
        
        if sayim['durum'] == SayimDurumu.IPTAL_EDILDI:
            raise StokSayimError("İptal edilmiş sayım tamamlanamaz")
        
        farklar = {}
        
        # Sayılan ürünler için fark hesapla
        for urun_id, sayilan_miktar in sayim['sayim_verileri'].items():
            sistem_miktar = sayim['sistem_bakiyeleri'].get(urun_id, Decimal('0'))
            fark = sayilan_miktar - sistem_miktar
            
            if fark != 0:
                farklar[urun_id] = fark
                
                # Sayım hareketi oluştur
                hareket = StokHareketDTO(
                    urun_id=urun_id,
                    magaza_id=sayim['magaza_id'],
                    depo_id=sayim['depo_id'],
                    hareket_tipi="SAYIM",
                    miktar=fark,
                    aciklama=f"Sayım farkı - Sayım ID: {sayim_id}",
                    kullanici_id=sayim['kullanici_id'],
                    referans_tablo="stok_sayimlari",
                    referans_id=None  # Sayım tablosu ID'si olabilir
                )
                
                # Hareketi kaydet
                self._hareket_repository.hareket_ekle(hareket)
                
                # Bakiyeyi güncelle
                mevcut_bakiye = self._bakiye_repository.bakiye_getir(
                    urun_id, sayim['magaza_id'], sayim['depo_id']
                )
                
                if mevcut_bakiye:
                    yeni_miktar = mevcut_bakiye.miktar + fark
                    yeni_kullanilabilir = mevcut_bakiye.kullanilabilir_miktar + fark
                    
                    self._bakiye_repository.bakiye_guncelle(
                        mevcut_bakiye.id,
                        yeni_miktar,
                        mevcut_bakiye.rezerve_miktar,
                        yeni_kullanilabilir,
                        None,  # birim_fiyat
                        datetime.utcnow()
                    )
        
        # Sayımı tamamla
        sayim['durum'] = SayimDurumu.TAMAMLANDI
        sayim['tamamlanma_tarihi'] = datetime.utcnow()
        sayim['farklar'] = farklar
        
        return farklar
    
    def sayim_iptal(self, sayim_id: str) -> None:
        """
        Sayım işlemini iptal eder
        
        Args:
            sayim_id: Sayım ID
            
        Raises:
            StokSayimError: Sayım hatası durumunda
        """
        if sayim_id not in self._aktif_sayimlar:
            raise StokSayimError(f"Aktif sayım bulunamadı: {sayim_id}")
        
        sayim = self._aktif_sayimlar[sayim_id]
        
        if sayim['durum'] == SayimDurumu.TAMAMLANDI:
            raise StokSayimError("Tamamlanmış sayım iptal edilemez")
        
        if sayim['durum'] == SayimDurumu.IPTAL_EDILDI:
            raise StokSayimError("Sayım zaten iptal edilmiş")
        
        # Sayımı iptal et
        sayim['durum'] = SayimDurumu.IPTAL_EDILDI
        sayim['iptal_tarihi'] = datetime.utcnow()
    
    def sayim_durumu_getir(self, sayim_id: str) -> Dict:
        """
        Sayım durumunu getirir
        
        Args:
            sayim_id: Sayım ID
            
        Returns:
            Dict: Sayım durumu bilgileri
            
        Raises:
            StokSayimError: Sayım bulunamadığında
        """
        if sayim_id not in self._aktif_sayimlar:
            raise StokSayimError(f"Sayım bulunamadı: {sayim_id}")
        
        return self._aktif_sayimlar[sayim_id].copy()
    
    def aktif_sayimlar_listesi(self, magaza_id: Optional[int] = None) -> List[Dict]:
        """
        Aktif sayımların listesini getirir
        
        Args:
            magaza_id: Mağaza ID filtresi (opsiyonel)
            
        Returns:
            List[Dict]: Aktif sayımlar listesi
        """
        sayimlar = []
        
        for sayim in self._aktif_sayimlar.values():
            if magaza_id is None or sayim['magaza_id'] == magaza_id:
                if sayim['durum'] in [SayimDurumu.BASLADI, SayimDurumu.DEVAM_EDIYOR]:
                    sayimlar.append(sayim.copy())
        
        return sayimlar