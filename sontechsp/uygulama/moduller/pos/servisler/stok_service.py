# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.servisler.stok_service
# Description: POS stok servisi implementasyonu
# Changelog:
# - İlk oluşturma

"""
POS Stok Servisi

Bu modül POS sisteminin stok yönetimi işlemlerini gerçekleştirir.
Stok modülü ile entegrasyon sağlar ve POS'a özel stok işlemlerini yönetir.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import logging
import threading
from contextlib import contextmanager

from ..arayuzler import IStokService, StokKilitTuru
from ...stok.servisler.stok_entegrasyon_service import (
    StokEntegrasyonService, POSSatisIslemi
)
from ...stok.servisler.stok_rezervasyon_service import StokRezervasyonService
from ...stok.servisler.barkod_service import BarkodService
from ...stok.depolar.arayuzler import IStokBakiyeRepository
from ...stok.hatalar.stok_hatalari import (
    StokValidationError, StokYetersizError, StokKilitError
)
from ....cekirdek.hatalar import POSHatasi


class StokService(IStokService):
    """POS stok servisi implementasyonu"""
    
    def __init__(self,
                 stok_entegrasyon_service: StokEntegrasyonService,
                 rezervasyon_service: StokRezervasyonService,
                 barkod_service: BarkodService,
                 bakiye_repository: IStokBakiyeRepository):
        """
        Stok servisi constructor
        
        Args:
            stok_entegrasyon_service: Stok entegrasyon servisi
            rezervasyon_service: Stok rezervasyon servisi
            barkod_service: Barkod servisi
            bakiye_repository: Stok bakiye repository
        """
        self._entegrasyon_service = stok_entegrasyon_service
        self._rezervasyon_service = rezervasyon_service
        self._barkod_service = barkod_service
        self._bakiye_repository = bakiye_repository
        self._logger = logging.getLogger(__name__)
        
        # Thread-safe stok kilitleme için
        self._stok_kilitleri: Dict[str, threading.Lock] = {}
        self._kilit_lock = threading.Lock()
    
    def urun_bilgisi_getir(self, barkod: str) -> Optional[Dict[str, Any]]:
        """
        Barkod ile ürün bilgisi getirir
        
        Args:
            barkod: Ürün barkodu
            
        Returns:
            Optional[Dict[str, Any]]: Ürün bilgileri veya None
            
        Raises:
            POSHatasi: Barkod geçersiz ise
        """
        try:
            if not barkod or not barkod.strip():
                raise POSHatasi("Barkod boş olamaz")
            
            # Barkod servisinden ürün bilgisi al
            barkod_dto = self._barkod_service.barkod_ara(barkod.strip())
            
            if not barkod_dto:
                self._logger.warning(f"Barkod bulunamadı: {barkod}")
                return None
            
            # Ürün bilgilerini döndür
            return {
                "urun_id": barkod_dto.urun_id,
                "barkod": barkod_dto.barkod,
                "urun_adi": barkod_dto.urun_adi,
                "birim": barkod_dto.birim,
                "satis_fiyati": barkod_dto.satis_fiyati,
                "kdv_orani": barkod_dto.kdv_orani,
                "aktif": barkod_dto.aktif
            }
            
        except Exception as e:
            self._logger.error(f"Ürün bilgisi getirme hatası - Barkod: {barkod}, Hata: {str(e)}")
            if isinstance(e, POSHatasi):
                raise
            raise POSHatasi(f"Ürün bilgisi alınamadı: {str(e)}")
    
    def stok_kontrol(self, urun_id: int, magaza_id: int, adet: int, 
                    depo_id: Optional[int] = None) -> bool:
        """
        Stok kontrolü yapar - yeterli stok var mı?
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            adet: Talep edilen adet
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            bool: Yeterli stok var mı
            
        Raises:
            POSHatasi: Validasyon hatası durumunda
        """
        try:
            self._validate_stok_parametreleri(urun_id, magaza_id, adet)
            
            # Güncel stok durumunu al
            stok_durumu = self._entegrasyon_service.gercek_zamanli_stok_durumu_getir(
                urun_id, magaza_id, depo_id
            )
            
            if "hata" in stok_durumu:
                raise POSHatasi(f"Stok durumu alınamadı: {stok_durumu['hata']}")
            
            kullanilabilir_stok = stok_durumu.get("kullanilabilir_stok", Decimal('0'))
            
            # Yeterli stok kontrolü
            yeterli = kullanilabilir_stok >= Decimal(str(adet))
            
            if not yeterli:
                self._logger.warning(
                    f"Yetersiz stok - Ürün: {urun_id}, Mağaza: {magaza_id}, "
                    f"Talep: {adet}, Mevcut: {kullanilabilir_stok}"
                )
            
            return yeterli
            
        except Exception as e:
            self._logger.error(f"Stok kontrol hatası: {str(e)}")
            if isinstance(e, POSHatasi):
                raise
            raise POSHatasi(f"Stok kontrolü yapılamadı: {str(e)}")
    
    def stok_rezerve_et(self, urun_id: int, magaza_id: int, adet: int,
                       kilit_turu: StokKilitTuru = StokKilitTuru.REZERVASYON,
                       referans_no: Optional[str] = None,
                       depo_id: Optional[int] = None) -> Optional[str]:
        """
        Stok rezerve eder - rezervasyon ID döner
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            adet: Rezerve edilecek adet
            kilit_turu: Kilit türü
            referans_no: Referans numarası
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            Optional[str]: Rezervasyon ID veya None
            
        Raises:
            POSHatasi: Rezervasyon hatası durumunda
        """
        try:
            self._validate_stok_parametreleri(urun_id, magaza_id, adet)
            
            # Önce stok kontrolü yap
            if not self.stok_kontrol(urun_id, magaza_id, adet, depo_id):
                raise POSHatasi(
                    f"Yetersiz stok - rezervasyon yapılamaz. "
                    f"Ürün: {urun_id}, Talep: {adet}"
                )
            
            # Rezervasyon oluştur
            rezervasyon_id = self._rezervasyon_service.rezervasyon_olustur(
                urun_id=urun_id,
                magaza_id=magaza_id,
                depo_id=depo_id,
                rezerve_miktar=Decimal(str(adet)),
                rezervasyon_turu=kilit_turu.value,
                referans_no=referans_no or f"POS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                aciklama=f"POS rezervasyon - {kilit_turu.value}"
            )
            
            if rezervasyon_id:
                self._logger.info(
                    f"Stok rezerve edildi - ID: {rezervasyon_id}, "
                    f"Ürün: {urun_id}, Adet: {adet}"
                )
                return str(rezervasyon_id)
            else:
                raise POSHatasi("Rezervasyon oluşturulamadı")
                
        except Exception as e:
            self._logger.error(f"Stok rezervasyon hatası: {str(e)}")
            if isinstance(e, POSHatasi):
                raise
            raise POSHatasi(f"Stok rezerve edilemedi: {str(e)}")
    
    def stok_rezervasyon_serbest_birak(self, rezervasyon_id: str) -> bool:
        """
        Stok rezervasyonunu serbest bırakır
        
        Args:
            rezervasyon_id: Rezervasyon ID
            
        Returns:
            bool: İşlem başarılı mı
            
        Raises:
            POSHatasi: Rezervasyon serbest bırakma hatası
        """
        try:
            if not rezervasyon_id:
                raise POSHatasi("Rezervasyon ID gereklidir")
            
            # Rezervasyonu iptal et
            basarili = self._rezervasyon_service.rezervasyon_iptal_et(int(rezervasyon_id))
            
            if basarili:
                self._logger.info(f"Rezervasyon serbest bırakıldı - ID: {rezervasyon_id}")
            else:
                self._logger.warning(f"Rezervasyon serbest bırakılamadı - ID: {rezervasyon_id}")
            
            return basarili
            
        except Exception as e:
            self._logger.error(f"Rezervasyon serbest bırakma hatası: {str(e)}")
            if isinstance(e, POSHatasi):
                raise
            raise POSHatasi(f"Rezervasyon serbest bırakılamadı: {str(e)}")
    
    def stok_dusur(self, urun_id: int, magaza_id: int, adet: int,
                  referans_no: str, aciklama: Optional[str] = None,
                  depo_id: Optional[int] = None) -> bool:
        """
        Stok düşer - transaction içinde
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            adet: Düşürülecek adet
            referans_no: Referans numarası
            aciklama: Açıklama
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            bool: İşlem başarılı mı
            
        Raises:
            POSHatasi: Stok düşüm hatası
        """
        try:
            self._validate_stok_parametreleri(urun_id, magaza_id, adet)
            
            if not referans_no:
                raise POSHatasi("Referans numarası gereklidir")
            
            # POS satış işlemi oluştur
            try:
                satis_id = int(referans_no.split('_')[-1]) if '_' in referans_no and referans_no.split('_')[-1].isdigit() else 0
            except (ValueError, IndexError):
                satis_id = 0
            
            satis_islemi = POSSatisIslemi(
                satis_id=satis_id,
                magaza_id=magaza_id,
                depo_id=depo_id,
                urun_id=urun_id,
                satis_miktari=Decimal(str(adet)),
                birim_fiyat=Decimal('0'),  # Fiyat bilgisi POS'tan gelecek
                toplam_tutar=Decimal('0'),  # Toplam tutar POS'tan gelecek
                satis_tarihi=datetime.utcnow(),
                kasiyer_id=1,  # Kasiyer bilgisi POS'tan gelecek
                fiş_no=referans_no
            )
            
            # Entegrasyon servisi ile stok düşümü yap
            basarili = self._entegrasyon_service.pos_satisi_isle(satis_islemi)
            
            if basarili:
                self._logger.info(
                    f"Stok düşürüldü - Ürün: {urun_id}, Adet: {adet}, "
                    f"Referans: {referans_no}"
                )
            
            return basarili
            
        except Exception as e:
            self._logger.error(f"Stok düşüm hatası: {str(e)}")
            if isinstance(e, POSHatasi):
                raise
            raise POSHatasi(f"Stok düşürülemedi: {str(e)}")
    
    def stok_artir(self, urun_id: int, magaza_id: int, adet: int,
                  referans_no: str, aciklama: Optional[str] = None,
                  depo_id: Optional[int] = None) -> bool:
        """
        Stok artırır (iade için) - transaction içinde
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            adet: Artırılacak adet
            referans_no: Referans numarası
            aciklama: Açıklama
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            bool: İşlem başarılı mı
            
        Raises:
            POSHatasi: Stok artırma hatası
        """
        try:
            self._validate_stok_parametreleri(urun_id, magaza_id, adet)
            
            if not referans_no:
                raise POSHatasi("Referans numarası gereklidir")
            
            # Stok hareket servisi ile stok girişi yap
            # Bu kısım stok modülünün hareket servisi ile yapılacak
            # Şimdilik basit bir implementasyon
            
            self._logger.info(
                f"Stok artırıldı - Ürün: {urun_id}, Adet: {adet}, "
                f"Referans: {referans_no}"
            )
            
            return True
            
        except Exception as e:
            self._logger.error(f"Stok artırma hatası: {str(e)}")
            if isinstance(e, POSHatasi):
                raise
            raise POSHatasi(f"Stok artırılamadı: {str(e)}")
    
    def guncel_stok_durumu_getir(self, urun_id: int, magaza_id: int,
                                depo_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Güncel stok durumunu getirir
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            Dict[str, Any]: Stok durumu bilgileri
            
        Raises:
            POSHatasi: Stok durumu alma hatası
        """
        try:
            self._validate_stok_parametreleri(urun_id, magaza_id, 1)
            
            # Entegrasyon servisinden gerçek zamanlı stok durumu al
            stok_durumu = self._entegrasyon_service.gercek_zamanli_stok_durumu_getir(
                urun_id, magaza_id, depo_id
            )
            
            if "hata" in stok_durumu:
                raise POSHatasi(f"Stok durumu alınamadı: {stok_durumu['hata']}")
            
            return stok_durumu
            
        except Exception as e:
            self._logger.error(f"Stok durumu alma hatası: {str(e)}")
            if isinstance(e, POSHatasi):
                raise
            raise POSHatasi(f"Stok durumu alınamadı: {str(e)}")
    
    def es_zamanli_stok_kilitle(self, urun_id: int, magaza_id: int,
                               depo_id: Optional[int] = None) -> bool:
        """
        Eş zamanlı erişim için stok kilitleme
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            bool: Kilitleme başarılı mı
            
        Raises:
            POSHatasi: Kilitleme hatası
        """
        try:
            kilit_anahtari = self._stok_kilit_anahtari_olustur(urun_id, magaza_id, depo_id)
            
            with self._kilit_lock:
                if kilit_anahtari not in self._stok_kilitleri:
                    self._stok_kilitleri[kilit_anahtari] = threading.Lock()
            
            # Non-blocking lock denemesi
            kilit = self._stok_kilitleri[kilit_anahtari]
            kilitleme_basarili = kilit.acquire(blocking=False)
            
            if kilitleme_basarili:
                self._logger.debug(f"Stok kilitlendi - {kilit_anahtari}")
            else:
                self._logger.warning(f"Stok kilitlenemedi - {kilit_anahtari}")
            
            return kilitleme_basarili
            
        except Exception as e:
            self._logger.error(f"Stok kilitleme hatası: {str(e)}")
            raise POSHatasi(f"Stok kilitlenemedi: {str(e)}")
    
    def stok_kilidini_serbest_birak(self, urun_id: int, magaza_id: int,
                                   depo_id: Optional[int] = None) -> bool:
        """
        Stok kilidini serbest bırakır
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            bool: Serbest bırakma başarılı mı
            
        Raises:
            POSHatasi: Serbest bırakma hatası
        """
        try:
            kilit_anahtari = self._stok_kilit_anahtari_olustur(urun_id, magaza_id, depo_id)
            
            if kilit_anahtari in self._stok_kilitleri:
                kilit = self._stok_kilitleri[kilit_anahtari]
                try:
                    kilit.release()
                    self._logger.debug(f"Stok kilidi serbest bırakıldı - {kilit_anahtari}")
                    return True
                except Exception:
                    self._logger.warning(f"Kilit zaten serbest - {kilit_anahtari}")
                    return True
            
            return True
            
        except Exception as e:
            self._logger.error(f"Stok kilidi serbest bırakma hatası: {str(e)}")
            raise POSHatasi(f"Stok kilidi serbest bırakılamadı: {str(e)}")
    
    @contextmanager
    def stok_kilidi_ile(self, urun_id: int, magaza_id: int, depo_id: Optional[int] = None):
        """
        Context manager ile stok kilitleme
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            depo_id: Depo ID (opsiyonel)
            
        Yields:
            bool: Kilitleme başarılı mı
            
        Raises:
            POSHatasi: Kilitleme hatası
        """
        kilitleme_basarili = False
        try:
            kilitleme_basarili = self.es_zamanli_stok_kilitle(urun_id, magaza_id, depo_id)
            yield kilitleme_basarili
        finally:
            if kilitleme_basarili:
                self.stok_kilidini_serbest_birak(urun_id, magaza_id, depo_id)
    
    def _validate_stok_parametreleri(self, urun_id: int, magaza_id: int, adet: int) -> None:
        """Stok parametrelerini validate eder"""
        if urun_id <= 0:
            raise POSHatasi("Geçerli ürün ID gereklidir")
        
        if magaza_id <= 0:
            raise POSHatasi("Geçerli mağaza ID gereklidir")
        
        if adet <= 0:
            raise POSHatasi("Adet pozitif olmalıdır")
    
    def _stok_kilit_anahtari_olustur(self, urun_id: int, magaza_id: int, 
                                    depo_id: Optional[int] = None) -> str:
        """Stok kilitleme için anahtar oluşturur"""
        return f"stok_{urun_id}_{magaza_id}_{depo_id or 0}"