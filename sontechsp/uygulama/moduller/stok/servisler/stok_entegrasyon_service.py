# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.stok_entegrasyon_service
# Description: SONTECHSP stok entegrasyon servisi
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Entegrasyon Servisi

Bu modül stok sisteminin diğer modüllerle entegrasyonunu sağlar.
POS satış işlemleri ve e-ticaret güncellemeleri için gerçek zamanlı stok yönetimi yapar.
"""

from typing import List, Optional, Dict, Any, Callable
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass
import threading
import queue
import logging

from ..dto import StokHareketDTO, StokBakiyeDTO
from ..depolar.arayuzler import IStokHareketRepository, IStokBakiyeRepository
from ..hatalar.stok_hatalari import StokValidationError, StokYetersizError
from .arayuzler import IStokHareketService
from .stok_rezervasyon_service import StokRezervasyonService


@dataclass
class StokGuncellemeBildirimi:
    """Stok güncelleme bildirimi"""
    urun_id: int
    magaza_id: int
    depo_id: Optional[int]
    eski_miktar: Decimal
    yeni_miktar: Decimal
    hareket_tipi: str
    zaman_damgasi: datetime
    kaynak_modul: str  # 'POS', 'ETICARET', 'MANUEL'
    referans_no: Optional[str] = None


@dataclass
class POSSatisIslemi:
    """POS satış işlemi bilgileri"""
    satis_id: int
    magaza_id: int
    depo_id: Optional[int]
    urun_id: int
    satis_miktari: Decimal
    birim_fiyat: Decimal
    toplam_tutar: Decimal
    satis_tarihi: datetime
    kasiyer_id: int
    fiş_no: str


@dataclass
class EticaretGuncelleme:
    """E-ticaret güncelleme bilgileri"""
    platform: str  # 'TRENDYOL', 'HEPSIBURADA', 'N11', vb.
    urun_id: int
    magaza_id: int
    depo_id: Optional[int]
    yeni_stok_miktari: Decimal
    guncelleme_tarihi: datetime
    siparis_id: Optional[str] = None


class StokEntegrasyonService:
    """Stok entegrasyon servisi implementasyonu"""
    
    def __init__(self,
                 hareket_service: IStokHareketService,
                 bakiye_repository: IStokBakiyeRepository,
                 rezervasyon_service: StokRezervasyonService):
        """
        Stok entegrasyon servisi constructor
        
        Args:
            hareket_service: Stok hareket servisi
            bakiye_repository: Stok bakiye repository
            rezervasyon_service: Stok rezervasyon servisi
        """
        self._hareket_service = hareket_service
        self._bakiye_repository = bakiye_repository
        self._rezervasyon_service = rezervasyon_service
        self._logger = logging.getLogger(__name__)
        
        # Gerçek zamanlı güncelleme için event system
        self._guncelleme_dinleyicileri: List[Callable[[StokGuncellemeBildirimi], None]] = []
        self._guncelleme_kuyrugu = queue.Queue()
        self._guncelleme_thread = None
        self._thread_calisir = False
        
        # Entegrasyon durumu
        self._pos_entegrasyonu_aktif = True
        self._eticaret_entegrasyonu_aktif = True
        
        self._guncelleme_thread_baslat()
    
    def pos_satisi_isle(self, satis_islemi: POSSatisIslemi) -> bool:
        """
        POS satış işlemini işler ve otomatik stok düşümü yapar
        
        Args:
            satis_islemi: POS satış işlemi bilgileri
            
        Returns:
            bool: İşlem başarılı mı
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
            StokYetersizError: Yetersiz stok durumunda
        """
        if not self._pos_entegrasyonu_aktif:
            self._logger.warning("POS entegrasyonu devre dışı")
            return False
        
        try:
            # Validasyon
            self._validate_pos_satisi(satis_islemi)
            
            # Mevcut stok kontrolü
            mevcut_bakiye = self._bakiye_repository.bakiye_getir(
                satis_islemi.urun_id,
                satis_islemi.magaza_id,
                satis_islemi.depo_id
            )
            
            if not mevcut_bakiye:
                raise StokYetersizError(
                    "Ürün için stok kaydı bulunamadı",
                    urun_kodu=f"ID:{satis_islemi.urun_id}",
                    kullanilabilir_stok=Decimal('0'),
                    talep_edilen_miktar=satis_islemi.satis_miktari
                )
            
            kullanilabilir_stok = mevcut_bakiye.kullanilabilir_miktar
            
            if kullanilabilir_stok < satis_islemi.satis_miktari:
                raise StokYetersizError(
                    f"Yetersiz stok. Mevcut: {kullanilabilir_stok}, Satış: {satis_islemi.satis_miktari}",
                    urun_kodu=f"ID:{satis_islemi.urun_id}",
                    kullanilabilir_stok=kullanilabilir_stok,
                    talep_edilen_miktar=satis_islemi.satis_miktari
                )
            
            # Stok hareket kaydı oluştur
            hareket = StokHareketDTO(
                urun_id=satis_islemi.urun_id,
                magaza_id=satis_islemi.magaza_id,
                depo_id=satis_islemi.depo_id,
                hareket_tipi="CIKIS",
                miktar=satis_islemi.satis_miktari,
                birim_fiyat=satis_islemi.birim_fiyat,
                aciklama=f"POS Satış - Fiş No: {satis_islemi.fiş_no}",
                referans_no=f"POS_{satis_islemi.satis_id}",
                kullanici_id=satis_islemi.kasiyer_id,
                hareket_tarihi=satis_islemi.satis_tarihi
            )
            
            # Stok çıkışı yap
            hareket_id = self._hareket_service.stok_cikisi(hareket)
            
            # Gerçek zamanlı güncelleme bildirimi gönder
            bildirim = StokGuncellemeBildirimi(
                urun_id=satis_islemi.urun_id,
                magaza_id=satis_islemi.magaza_id,
                depo_id=satis_islemi.depo_id,
                eski_miktar=kullanilabilir_stok,
                yeni_miktar=kullanilabilir_stok - satis_islemi.satis_miktari,
                hareket_tipi="POS_SATIS",
                zaman_damgasi=datetime.utcnow(),
                kaynak_modul="POS",
                referans_no=f"POS_{satis_islemi.satis_id}"
            )
            
            self._guncelleme_bildir(bildirim)
            
            self._logger.info(
                f"POS satış işlendi - Ürün: {satis_islemi.urun_id}, "
                f"Miktar: {satis_islemi.satis_miktari}, Hareket ID: {hareket_id}"
            )
            
            return True
            
        except Exception as e:
            self._logger.error(f"POS satış işlemi hatası: {str(e)}")
            raise
    
    def eticaret_guncelle(self, guncelleme: EticaretGuncelleme) -> bool:
        """
        E-ticaret platformu stok güncellemesi yapar
        
        Args:
            guncelleme: E-ticaret güncelleme bilgileri
            
        Returns:
            bool: Güncelleme başarılı mı
            
        Raises:
            StokValidationError: Validasyon hatası durumunda
        """
        if not self._eticaret_entegrasyonu_aktif:
            self._logger.warning("E-ticaret entegrasyonu devre dışı")
            return False
        
        try:
            # Validasyon
            self._validate_eticaret_guncelleme(guncelleme)
            
            # Mevcut stok durumunu al
            mevcut_bakiye = self._bakiye_repository.bakiye_getir(
                guncelleme.urun_id,
                guncelleme.magaza_id,
                guncelleme.depo_id
            )
            
            if not mevcut_bakiye:
                self._logger.warning(
                    f"E-ticaret güncelleme için stok kaydı bulunamadı - "
                    f"Ürün: {guncelleme.urun_id}, Platform: {guncelleme.platform}"
                )
                return False
            
            eski_miktar = mevcut_bakiye.kullanilabilir_miktar
            
            # E-ticaret platformuna güncel stok bilgisini gönder
            # (Bu kısım gerçek entegrasyon kodları ile değiştirilecek)
            guncelleme_basarili = self._eticaret_platformu_guncelle(
                guncelleme.platform,
                guncelleme.urun_id,
                guncelleme.yeni_stok_miktari
            )
            
            if guncelleme_basarili:
                # Gerçek zamanlı güncelleme bildirimi gönder
                bildirim = StokGuncellemeBildirimi(
                    urun_id=guncelleme.urun_id,
                    magaza_id=guncelleme.magaza_id,
                    depo_id=guncelleme.depo_id,
                    eski_miktar=eski_miktar,
                    yeni_miktar=guncelleme.yeni_stok_miktari,
                    hareket_tipi="ETICARET_GUNCELLEME",
                    zaman_damgasi=datetime.utcnow(),
                    kaynak_modul="ETICARET",
                    referans_no=f"{guncelleme.platform}_{guncelleme.siparis_id or 'SYNC'}"
                )
                
                self._guncelleme_bildir(bildirim)
                
                self._logger.info(
                    f"E-ticaret güncelleme başarılı - Platform: {guncelleme.platform}, "
                    f"Ürün: {guncelleme.urun_id}, Yeni Stok: {guncelleme.yeni_stok_miktari}"
                )
            
            return guncelleme_basarili
            
        except Exception as e:
            self._logger.error(f"E-ticaret güncelleme hatası: {str(e)}")
            return False
    
    def gercek_zamanli_stok_durumu_getir(self, 
                                       urun_id: int, 
                                       magaza_id: int,
                                       depo_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gerçek zamanlı stok durumu bilgilerini getirir
        
        Args:
            urun_id: Ürün ID
            magaza_id: Mağaza ID
            depo_id: Depo ID (opsiyonel)
            
        Returns:
            Dict[str, Any]: Stok durumu bilgileri
        """
        try:
            # Mevcut bakiye bilgisi
            bakiye = self._bakiye_repository.bakiye_getir(urun_id, magaza_id, depo_id)
            
            if not bakiye:
                return {
                    "urun_id": urun_id,
                    "magaza_id": magaza_id,
                    "depo_id": depo_id,
                    "toplam_stok": Decimal('0'),
                    "rezerve_stok": Decimal('0'),
                    "kullanilabilir_stok": Decimal('0'),
                    "son_guncelleme": None,
                    "durum": "STOK_YOK"
                }
            
            # Aktif rezervasyonları al
            aktif_rezervasyonlar = self._rezervasyon_service.aktif_rezervasyonlar_listesi(
                urun_id=urun_id,
                magaza_id=magaza_id
            )
            
            toplam_rezerve = sum(r.rezerve_miktar for r in aktif_rezervasyonlar)
            
            # Stok durumunu belirle
            durum = "NORMAL"
            if bakiye.kullanilabilir_miktar <= 0:
                durum = "STOK_YOK"
            elif bakiye.kullanilabilir_miktar <= Decimal('10'):  # Kritik seviye
                durum = "KRITIK"
            
            return {
                "urun_id": urun_id,
                "magaza_id": magaza_id,
                "depo_id": depo_id,
                "toplam_stok": bakiye.miktar,
                "rezerve_stok": toplam_rezerve,
                "kullanilabilir_stok": bakiye.kullanilabilir_miktar,
                "son_guncelleme": bakiye.son_hareket_tarihi,
                "durum": durum,
                "aktif_rezervasyon_sayisi": len(aktif_rezervasyonlar)
            }
            
        except Exception as e:
            self._logger.error(f"Gerçek zamanlı stok durumu hatası: {str(e)}")
            return {
                "urun_id": urun_id,
                "magaza_id": magaza_id,
                "depo_id": depo_id,
                "hata": str(e)
            }
    
    def guncelleme_dinleyicisi_ekle(self, dinleyici: Callable[[StokGuncellemeBildirimi], None]) -> None:
        """
        Stok güncelleme dinleyicisi ekler
        
        Args:
            dinleyici: Güncelleme bildirimi dinleyici fonksiyonu
        """
        if dinleyici not in self._guncelleme_dinleyicileri:
            self._guncelleme_dinleyicileri.append(dinleyici)
    
    def guncelleme_dinleyicisi_kaldir(self, dinleyici: Callable[[StokGuncellemeBildirimi], None]) -> None:
        """
        Stok güncelleme dinleyicisini kaldırır
        
        Args:
            dinleyici: Kaldırılacak dinleyici fonksiyonu
        """
        if dinleyici in self._guncelleme_dinleyicileri:
            self._guncelleme_dinleyicileri.remove(dinleyici)
    
    def entegrasyon_durumu_getir(self) -> Dict[str, Any]:
        """
        Entegrasyon durumu bilgilerini getirir
        
        Returns:
            Dict[str, Any]: Entegrasyon durumu
        """
        return {
            "pos_entegrasyonu": {
                "aktif": self._pos_entegrasyonu_aktif,
                "durum": "ÇALIŞIYOR" if self._pos_entegrasyonu_aktif else "DEVRE_DIŞI"
            },
            "eticaret_entegrasyonu": {
                "aktif": self._eticaret_entegrasyonu_aktif,
                "durum": "ÇALIŞIYOR" if self._eticaret_entegrasyonu_aktif else "DEVRE_DIŞI"
            },
            "guncelleme_sistemi": {
                "aktif": self._thread_calisir,
                "dinleyici_sayisi": len(self._guncelleme_dinleyicileri),
                "kuyruk_boyutu": self._guncelleme_kuyrugu.qsize()
            }
        }
    
    def pos_entegrasyonu_ayarla(self, aktif: bool) -> None:
        """POS entegrasyonunu aktif/pasif yapar"""
        self._pos_entegrasyonu_aktif = aktif
        self._logger.info(f"POS entegrasyonu {'aktif' if aktif else 'pasif'} edildi")
    
    def eticaret_entegrasyonu_ayarla(self, aktif: bool) -> None:
        """E-ticaret entegrasyonunu aktif/pasif yapar"""
        self._eticaret_entegrasyonu_aktif = aktif
        self._logger.info(f"E-ticaret entegrasyonu {'aktif' if aktif else 'pasif'} edildi")
    
    def kapat(self) -> None:
        """Servisi kapatır ve thread'leri temizler"""
        self._thread_calisir = False
        if self._guncelleme_thread and self._guncelleme_thread.is_alive():
            self._guncelleme_thread.join(timeout=5)
    
    def _validate_pos_satisi(self, satis_islemi: POSSatisIslemi) -> None:
        """POS satış işlemi validasyonu"""
        if satis_islemi.urun_id <= 0:
            raise StokValidationError("Geçerli ürün ID gereklidir")
        
        if satis_islemi.magaza_id <= 0:
            raise StokValidationError("Geçerli mağaza ID gereklidir")
        
        if satis_islemi.satis_miktari <= 0:
            raise StokValidationError("Satış miktarı pozitif olmalıdır")
        
        if not satis_islemi.fiş_no:
            raise StokValidationError("Fiş numarası gereklidir")
    
    def _validate_eticaret_guncelleme(self, guncelleme: EticaretGuncelleme) -> None:
        """E-ticaret güncelleme validasyonu"""
        if not guncelleme.platform:
            raise StokValidationError("Platform bilgisi gereklidir")
        
        if guncelleme.urun_id <= 0:
            raise StokValidationError("Geçerli ürün ID gereklidir")
        
        if guncelleme.magaza_id <= 0:
            raise StokValidationError("Geçerli mağaza ID gereklidir")
        
        if guncelleme.yeni_stok_miktari < 0:
            raise StokValidationError("Stok miktarı negatif olamaz")
    
    def _eticaret_platformu_guncelle(self, platform: str, urun_id: int, stok_miktari: Decimal) -> bool:
        """
        E-ticaret platformu güncelleme (placeholder)
        Gerçek implementasyonda platform API'leri kullanılacak
        """
        # Placeholder - gerçek entegrasyon kodları burada olacak
        self._logger.info(
            f"E-ticaret platform güncelleme simülasyonu - "
            f"Platform: {platform}, Ürün: {urun_id}, Stok: {stok_miktari}"
        )
        return True
    
    def _guncelleme_bildir(self, bildirim: StokGuncellemeBildirimi) -> None:
        """Güncelleme bildirimini kuyruğa ekler"""
        try:
            self._guncelleme_kuyrugu.put_nowait(bildirim)
        except queue.Full:
            self._logger.warning("Güncelleme kuyruğu dolu, bildirim atlandı")
    
    def _guncelleme_thread_baslat(self) -> None:
        """Güncelleme thread'ini başlatır"""
        if self._guncelleme_thread is None or not self._guncelleme_thread.is_alive():
            self._thread_calisir = True
            self._guncelleme_thread = threading.Thread(
                target=self._guncelleme_thread_calistir,
                daemon=True
            )
            self._guncelleme_thread.start()
    
    def _guncelleme_thread_calistir(self) -> None:
        """Güncelleme thread'i ana döngüsü"""
        while self._thread_calisir:
            try:
                # 1 saniye timeout ile bildirim bekle
                bildirim = self._guncelleme_kuyrugu.get(timeout=1)
                
                # Tüm dinleyicilere bildirim gönder
                for dinleyici in self._guncelleme_dinleyicileri:
                    try:
                        dinleyici(bildirim)
                    except Exception as e:
                        self._logger.error(f"Dinleyici hatası: {str(e)}")
                
                self._guncelleme_kuyrugu.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self._logger.error(f"Güncelleme thread hatası: {str(e)}")