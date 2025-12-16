# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.stok_yonetim_service
# Description: Ana stok yönetim koordinatörü
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Ana Stok Yönetim Servisi

Bu modül tüm stok servislerini koordine eden ana servis sınıfıdır.
Servisler arası entegrasyon ve iş akışı yönetimi yapar.
"""

from typing import List, Optional
from decimal import Decimal

from ..dto import UrunDTO, BarkodDTO, StokHareketDTO
from ..hatalar import StokHatasiBase
from .urun_service import UrunService
from .arayuzler import IUrunService, IBarkodService, IStokHareketService


class StokYonetimService:
    """Ana stok yönetim koordinatörü"""
    
    def __init__(
        self,
        urun_service: Optional[IUrunService] = None,
        barkod_service: Optional[IBarkodService] = None,
        stok_hareket_service: Optional[IStokHareketService] = None
    ):
        self.urun_service = urun_service or UrunService()
        self.barkod_service = barkod_service
        self.stok_hareket_service = stok_hareket_service
    
    def urun_ekle_ve_barkod_ata(self, urun: UrunDTO, barkod: BarkodDTO) -> int:
        """Ürün ekler ve barkod atar (tek işlem)"""
        try:
            # Ürün ekle
            urun_id = self.urun_service.urun_ekle(urun)
            
            # Barkod ata
            if self.barkod_service:
                barkod.urun_id = urun_id
                barkod.ana_barkod = True
                self.barkod_service.barkod_ekle(barkod)
            
            return urun_id
            
        except StokHatasiBase as e:
            # Hata durumunda rollback gerekebilir
            raise e
        except Exception as e:
            raise StokHatasiBase(f"Ürün ve barkod ekleme hatası: {str(e)}")
    
    def stok_hareket_yap_ve_bakiye_guncelle(
        self, 
        hareket: StokHareketDTO
    ) -> int:
        """Stok hareketi yapar ve bakiyeyi günceller"""
        try:
            if not self.stok_hareket_service:
                raise StokHatasiBase("Stok hareket servisi bulunamadı")
            
            # Hareket türüne göre işlem yap
            if hareket.hareket_tipi == "GIRIS":
                return self.stok_hareket_service.stok_girisi(hareket)
            elif hareket.hareket_tipi == "CIKIS":
                return self.stok_hareket_service.stok_cikisi(hareket)
            else:
                raise StokHatasiBase(f"Desteklenmeyen hareket türü: {hareket.hareket_tipi}")
                
        except StokHatasiBase:
            raise
        except Exception as e:
            raise StokHatasiBase(f"Stok hareket işlemi hatası: {str(e)}")
    
    def urun_ara_detayli(self, arama_terimi: str) -> List[dict]:
        """Ürün arar ve detaylı bilgi döner"""
        try:
            urunler = self.urun_service.urun_ara(arama_terimi)
            
            detayli_sonuclar = []
            for urun in urunler:
                sonuc = {
                    "urun": urun,
                    "barkodlar": [],
                    "stok_durumu": None
                }
                
                # Barkodları getir
                if self.barkod_service and urun.id:
                    sonuc["barkodlar"] = self.barkod_service.urun_barkodlari_getir(urun.id)
                
                detayli_sonuclar.append(sonuc)
            
            return detayli_sonuclar
            
        except Exception as e:
            raise StokHatasiBase(f"Detaylı arama hatası: {str(e)}")
    
    def sistem_durumu_kontrol(self) -> dict:
        """Sistem durumu kontrolü yapar"""
        try:
            durum = {
                "urun_servisi": self.urun_service is not None,
                "barkod_servisi": self.barkod_service is not None,
                "stok_hareket_servisi": self.stok_hareket_service is not None,
                "sistem_hazir": True
            }
            
            # Temel kontroller
            if not durum["urun_servisi"]:
                durum["sistem_hazir"] = False
            
            return durum
            
        except Exception as e:
            return {
                "sistem_hazir": False,
                "hata": str(e)
            }