# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.stok_hareket_service
# Description: SONTECHSP stok hareket servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Hareket Servisi

Bu modül stok hareket işlemlerini yöneten servis sınıfını içerir.
Stok giriş, çıkış ve hareket listesi işlemlerini gerçekleştirir.
"""

from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from ..dto import StokHareketDTO, StokHareketFiltreDTO
from ..depolar.arayuzler import IStokHareketRepository, IStokBakiyeRepository
from ..hatalar.stok_hatalari import StokValidationError, NegatifStokError
from .arayuzler import IStokHareketService, INegatifStokKontrol
from .negatif_stok_kontrol import NegatifStokKontrol


class StokHareketService(IStokHareketService):
    """Stok hareket servisi implementasyonu"""
    
    def __init__(self, 
                 hareket_repository: IStokHareketRepository,
                 bakiye_repository: IStokBakiyeRepository,
                 negatif_stok_kontrol: Optional[INegatifStokKontrol] = None):
        """
        Stok hareket servisi constructor
        
        Args:
            hareket_repository: Stok hareket repository
            bakiye_repository: Stok bakiye repository
            negatif_stok_kontrol: Negatif stok kontrol servisi
        """
        self._hareket_repository = hareket_repository
        self._bakiye_repository = bakiye_repository
        self._negatif_stok_kontrol = negatif_stok_kontrol or NegatifStokKontrol()
    
    def stok_girisi(self, hareket: StokHareketDTO) -> int:
        """
        Stok giriş işlemi gerçekleştirir
        
        Args:
            hareket: Stok hareket bilgileri
            
        Returns:
            int: Oluşturulan hareket ID
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        # Validasyon
        self._validate_hareket(hareket)
        
        # Giriş hareketi pozitif miktar olmalı
        if hareket.miktar <= 0:
            raise StokValidationError("Giriş hareketi pozitif miktar olmalıdır")
        
        # Hareket tipini ayarla
        hareket.hareket_tipi = "GIRIS"
        
        # Hareketi kaydet ve bakiyeyi güncelle
        return self._hareket_kaydet_ve_bakiye_guncelle(hareket)
    
    def stok_cikisi(self, hareket: StokHareketDTO) -> int:
        """
        Stok çıkış işlemi gerçekleştirir
        
        Args:
            hareket: Stok hareket bilgileri
            
        Returns:
            int: Oluşturulan hareket ID
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
            NegatifStokError: Negatif stok kontrolü başarısız olursa
        """
        # Validasyon
        self._validate_hareket(hareket)
        
        # Çıkış hareketi pozitif miktar olarak girilir, negatif olarak kaydedilir
        if hareket.miktar <= 0:
            raise StokValidationError("Çıkış hareketi pozitif miktar olmalıdır")
        
        # Mevcut stok bakiyesini al
        mevcut_bakiye = self._bakiye_repository.bakiye_getir(
            hareket.urun_id, 
            hareket.magaza_id, 
            hareket.depo_id
        )
        
        mevcut_stok = mevcut_bakiye.kullanilabilir_miktar if mevcut_bakiye else Decimal('0')
        
        # Negatif stok kontrolü
        if not self._negatif_stok_kontrol.kontrol_yap(
            hareket.urun_id, 
            hareket.miktar, 
            mevcut_stok
        ):
            raise NegatifStokError(
                f"Yetersiz stok. Mevcut: {mevcut_stok}, Talep: {hareket.miktar}"
            )
        
        # Hareket tipini ayarla ve miktarı negatif yap
        hareket.hareket_tipi = "CIKIS"
        hareket.miktar = -abs(hareket.miktar)
        
        # Hareketi kaydet ve bakiyeyi güncelle
        return self._hareket_kaydet_ve_bakiye_guncelle(hareket)
    
    def hareket_listesi(self, filtre: StokHareketFiltreDTO) -> List[StokHareketDTO]:
        """
        Stok hareket listesini getirir
        
        Args:
            filtre: Filtreleme kriterleri
            
        Returns:
            List[StokHareketDTO]: Hareket listesi
        """
        # Filtre validasyonu
        filtre_hatalari = filtre.validate()
        if filtre_hatalari:
            raise StokValidationError(f"Filtre hatası: {', '.join(filtre_hatalari)}")
        
        return self._hareket_repository.hareket_listesi(filtre)
    
    def _validate_hareket(self, hareket: StokHareketDTO) -> None:
        """
        Hareket validasyonu yapar
        
        Args:
            hareket: Validasyon yapılacak hareket
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        hatalar = hareket.validate()
        if hatalar:
            raise StokValidationError(f"Hareket validasyon hatası: {', '.join(hatalar)}")
    
    def _hareket_kaydet_ve_bakiye_guncelle(self, hareket: StokHareketDTO) -> int:
        """
        Hareketi kaydeder ve stok bakiyesini günceller
        
        Args:
            hareket: Kaydedilecek hareket
            
        Returns:
            int: Oluşturulan hareket ID
        """
        # Transaction içinde hareket kaydet ve bakiye güncelle
        hareket_id = self._hareket_repository.hareket_ekle(hareket)
        
        # Mevcut bakiyeyi al veya oluştur
        mevcut_bakiye = self._bakiye_repository.bakiye_getir(
            hareket.urun_id,
            hareket.magaza_id, 
            hareket.depo_id
        )
        
        if mevcut_bakiye:
            # Mevcut bakiyeyi güncelle
            yeni_miktar = mevcut_bakiye.miktar + hareket.miktar
            yeni_kullanilabilir = mevcut_bakiye.kullanilabilir_miktar + hareket.miktar
            
            self._bakiye_repository.bakiye_guncelle(
                mevcut_bakiye.id,
                yeni_miktar,
                mevcut_bakiye.rezerve_miktar,
                yeni_kullanilabilir,
                hareket.birim_fiyat,
                datetime.utcnow()
            )
        else:
            # Yeni bakiye oluştur
            from ..dto.stok_bakiye_dto import StokBakiyeDTO
            
            yeni_bakiye = StokBakiyeDTO(
                urun_id=hareket.urun_id,
                magaza_id=hareket.magaza_id,
                depo_id=hareket.depo_id,
                miktar=hareket.miktar,
                rezerve_miktar=Decimal('0'),
                kullanilabilir_miktar=hareket.miktar,
                son_hareket_tarihi=datetime.utcnow()
            )
            
            self._bakiye_repository.bakiye_ekle(yeni_bakiye)
        
        return hareket_id