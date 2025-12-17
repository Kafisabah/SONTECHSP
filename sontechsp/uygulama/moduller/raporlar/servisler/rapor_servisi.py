# Version: 0.1.0
# Last Update: 2024-12-17
# Module: raporlar.servisler.rapor_servisi
# Description: Raporlama modülü ana servis sınıfı
# Changelog:
# - İlk oluşturma
# - RaporServisi sınıfı eklendi
# - Tüm rapor metodları eklendi
# - Hata yönetimi ve loglama eklendi

"""
SONTECHSP Raporlar Ana Servis

Bu modül raporlama sisteminin ana servis sınıfını içerir:
- Satış özeti servisi
- Kritik stok servisi
- En çok satan ürünler servisi
- Karlılık servisi (MVP placeholder)
- Dışa aktarım servisi

Tüm iş mantığı bu katmanda uygulanır.
"""

import logging
import time
from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..dto import (
    TarihAraligiDTO, SatisOzetiDTO, UrunPerformansDTO, 
    KritikStokDTO, RaporSatirDTO, DisariAktarDTO
)
from ..sabitler import RaporSabitleri, HataMesajlari, LogMesajlari
from ..sorgular import satis_ozeti, kritik_stok_listesi, en_cok_satan_urunler, karlilik_ozeti
from ..disari_aktarim import disari_aktar, DosyaIslemHatasi
from ....veritabani.baglanti import get_readonly_session

logger = logging.getLogger(__name__)


class VeriTabaniHatasi(Exception):
    """Veritabanı hatası sınıfı"""
    pass


class ParametreHatasi(Exception):
    """Parametre hatası sınıfı"""
    pass


class VeriYokHatasi(Exception):
    """Veri bulunamadı hatası sınıfı"""
    pass


class RaporServisi:
    """Raporlama ana servis sınıfı"""
    
    def __init__(self):
        """Servis başlatıcı"""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _parametre_dogrula(self, magaza_id: Optional[int] = None, depo_id: Optional[int] = None, 
                          limit: Optional[int] = None) -> None:
        """
        Parametre doğrulaması yapar
        
        Args:
            magaza_id: Mağaza ID
            depo_id: Depo ID
            limit: Limit değeri
            
        Raises:
            ParametreHatasi: Geçersiz parametre durumunda
        """
        if magaza_id is not None and magaza_id <= 0:
            raise ParametreHatasi(HataMesajlari.GECERSIZ_MAGAZA_ID.format(magaza_id))
        
        if depo_id is not None and depo_id <= 0:
            raise ParametreHatasi(HataMesajlari.GECERSIZ_DEPO_ID.format(depo_id))
        
        if limit is not None and (limit < 1 or limit > RaporSabitleri.MAKSIMUM_LIMIT):
            raise ParametreHatasi(HataMesajlari.GECERSIZ_LIMIT.format(RaporSabitleri.MAKSIMUM_LIMIT))
    
    def _session_al(self) -> Session:
        """
        Salt okunur veritabanı oturumu alır
        
        Returns:
            Session: Salt okunur oturum
            
        Raises:
            VeriTabaniHatasi: Bağlantı hatası durumunda
        """
        try:
            return get_readonly_session()
        except Exception as e:
            hata_mesaji = HataMesajlari.VERITABANI_BAGLANTI_HATASI.format(str(e))
            self.logger.error(hata_mesaji)
            raise VeriTabaniHatasi(hata_mesaji)
    
    def satis_ozeti_al(self, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> SatisOzetiDTO:
        """
        Mağaza bazında satış özeti alır
        
        Args:
            magaza_id: Mağaza ID
            tarih_araligi: Tarih aralığı
            
        Returns:
            SatisOzetiDTO: Satış özeti verileri
            
        Raises:
            ParametreHatasi: Geçersiz parametre
            VeriTabaniHatasi: Veritabanı hatası
        """
        baslangic_zamani = time.time()
        
        try:
            # Parametre doğrulaması
            self._parametre_dogrula(magaza_id=magaza_id)
            
            self.logger.info(LogMesajlari.RAPOR_BASLATILDI.format("satis_ozeti", magaza_id))
            
            # Veritabanı oturumu al
            session = self._session_al()
            
            try:
                # Sorguyu çalıştır
                sonuc = satis_ozeti(session, magaza_id, tarih_araligi)
                
                # DTO'ya çevir
                satis_ozeti_dto = SatisOzetiDTO(
                    magaza_id=magaza_id,
                    brut_satis=sonuc['brut_satis'],
                    indirim_toplam=sonuc['indirim_toplam'],
                    net_satis=sonuc['net_satis'],
                    satis_adedi=sonuc['satis_adedi'],
                    iade_toplam=sonuc['iade_toplam']
                )
                
                # Performans loglaması
                gecen_sure = (time.time() - baslangic_zamani) * 1000
                self.logger.info(LogMesajlari.RAPOR_TAMAMLANDI.format("satis_ozeti", gecen_sure))
                
                return satis_ozeti_dto
                
            finally:
                session.close()
                
        except (ParametreHatasi, VeriTabaniHatasi):
            raise
        except SQLAlchemyError as e:
            hata_mesaji = HataMesajlari.SORGU_HATASI.format(str(e))
            self.logger.error(hata_mesaji)
            raise VeriTabaniHatasi(hata_mesaji)
        except Exception as e:
            hata_mesaji = HataMesajlari.BEKLENMEYEN_HATA.format(str(e))
            self.logger.error(hata_mesaji)
            raise
    
    def kritik_stok_al(self, depo_id: Optional[int] = None) -> List[KritikStokDTO]:
        """
        Kritik stok seviyesindeki ürünleri alır
        
        Args:
            depo_id: Opsiyonel depo ID filtresi
            
        Returns:
            List[KritikStokDTO]: Kritik stok ürün listesi
            
        Raises:
            ParametreHatasi: Geçersiz parametre
            VeriTabaniHatasi: Veritabanı hatası
        """
        baslangic_zamani = time.time()
        
        try:
            # Parametre doğrulaması
            if depo_id is not None:
                self._parametre_dogrula(depo_id=depo_id)
            
            self.logger.info(LogMesajlari.RAPOR_BASLATILDI.format("kritik_stok", depo_id or "tum_depolar"))
            
            # Veritabanı oturumu al
            session = self._session_al()
            
            try:
                # Sorguyu çalıştır
                sonuclar = kritik_stok_listesi(session, depo_id)
                
                # DTO listesine çevir
                kritik_stok_listesi_dto = [
                    KritikStokDTO(
                        urun_id=sonuc['urun_id'],
                        urun_adi=sonuc['urun_adi'],
                        depo_id=sonuc['depo_id'],
                        miktar=sonuc['miktar'],
                        kritik_seviye=sonuc['kritik_seviye']
                    )
                    for sonuc in sonuclar
                ]
                
                # Performans loglaması
                gecen_sure = (time.time() - baslangic_zamani) * 1000
                self.logger.info(LogMesajlari.RAPOR_TAMAMLANDI.format("kritik_stok", gecen_sure))
                
                return kritik_stok_listesi_dto
                
            finally:
                session.close()
                
        except (ParametreHatasi, VeriTabaniHatasi):
            raise
        except SQLAlchemyError as e:
            hata_mesaji = HataMesajlari.SORGU_HATASI.format(str(e))
            self.logger.error(hata_mesaji)
            raise VeriTabaniHatasi(hata_mesaji)
        except Exception as e:
            hata_mesaji = HataMesajlari.BEKLENMEYEN_HATA.format(str(e))
            self.logger.error(hata_mesaji)
            raise
    
    def en_cok_satan_al(self, magaza_id: int, tarih_araligi: TarihAraligiDTO, 
                       limit: int = RaporSabitleri.VARSAYILAN_LIMIT) -> List[UrunPerformansDTO]:
        """
        En çok satan ürünleri alır
        
        Args:
            magaza_id: Mağaza ID
            tarih_araligi: Tarih aralığı
            limit: Sonuç limiti
            
        Returns:
            List[UrunPerformansDTO]: En çok satan ürün listesi
            
        Raises:
            ParametreHatasi: Geçersiz parametre
            VeriTabaniHatasi: Veritabanı hatası
        """
        baslangic_zamani = time.time()
        
        try:
            # Parametre doğrulaması
            self._parametre_dogrula(magaza_id=magaza_id, limit=limit)
            
            self.logger.info(LogMesajlari.RAPOR_BASLATILDI.format("en_cok_satan", magaza_id))
            
            # Veritabanı oturumu al
            session = self._session_al()
            
            try:
                # Sorguyu çalıştır
                sonuclar = en_cok_satan_urunler(session, magaza_id, tarih_araligi, limit)
                
                # DTO listesine çevir
                urun_performans_listesi = [
                    UrunPerformansDTO(
                        urun_id=sonuc['urun_id'],
                        urun_adi=sonuc['urun_adi'],
                        miktar_toplam=sonuc['miktar_toplam'],
                        ciro_toplam=sonuc['ciro_toplam']
                    )
                    for sonuc in sonuclar
                ]
                
                # Performans loglaması
                gecen_sure = (time.time() - baslangic_zamani) * 1000
                self.logger.info(LogMesajlari.RAPOR_TAMAMLANDI.format("en_cok_satan", gecen_sure))
                
                return urun_performans_listesi
                
            finally:
                session.close()
                
        except (ParametreHatasi, VeriTabaniHatasi):
            raise
        except SQLAlchemyError as e:
            hata_mesaji = HataMesajlari.SORGU_HATASI.format(str(e))
            self.logger.error(hata_mesaji)
            raise VeriTabaniHatasi(hata_mesaji)
        except Exception as e:
            hata_mesaji = HataMesajlari.BEKLENMEYEN_HATA.format(str(e))
            self.logger.error(hata_mesaji)
            raise
    
    def karlilik_al(self, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> List[RaporSatirDTO]:
        """
        Karlılık raporunu alır (MVP placeholder)
        
        Args:
            magaza_id: Mağaza ID
            tarih_araligi: Tarih aralığı
            
        Returns:
            List[RaporSatirDTO]: Karlılık rapor satırları
            
        Note:
            Bu metod MVP'de placeholder olarak çalışır
        """
        baslangic_zamani = time.time()
        
        try:
            # Parametre doğrulaması
            self._parametre_dogrula(magaza_id=magaza_id)
            
            self.logger.warning(LogMesajlari.MVP_PLACEHOLDER_UYARISI.format("karlilik_al"))
            self.logger.info(LogMesajlari.RAPOR_BASLATILDI.format("karlilik", magaza_id))
            
            # Veritabanı oturumu al
            session = self._session_al()
            
            try:
                # Placeholder sorguyu çalıştır
                sonuclar = karlilik_ozeti(session, magaza_id, tarih_araligi)
                
                # DTO listesine çevir
                karlilik_listesi = [
                    RaporSatirDTO(
                        id=sonuc['urun_id'],
                        ad=sonuc['urun_adi'],
                        deger1=sonuc['maliyet'],
                        deger2=sonuc['kar_marji'],
                        deger3=sonuc['kar_tutari'],
                        aciklama="MVP placeholder - karlılık hesaplaması yapılmamıştır"
                    )
                    for sonuc in sonuclar
                ]
                
                # Performans loglaması
                gecen_sure = (time.time() - baslangic_zamani) * 1000
                self.logger.info(LogMesajlari.RAPOR_TAMAMLANDI.format("karlilik", gecen_sure))
                
                return karlilik_listesi
                
            finally:
                session.close()
                
        except (ParametreHatasi, VeriTabaniHatasi):
            raise
        except SQLAlchemyError as e:
            hata_mesaji = HataMesajlari.SORGU_HATASI.format(str(e))
            self.logger.error(hata_mesaji)
            raise VeriTabaniHatasi(hata_mesaji)
        except Exception as e:
            hata_mesaji = HataMesajlari.BEKLENMEYEN_HATA.format(str(e))
            self.logger.error(hata_mesaji)
            raise
    
    def disari_aktar(self, rapor_turu: str, veri: Any, disari_aktar_dto: DisariAktarDTO) -> str:
        """
        Raporu dışa aktarır
        
        Args:
            rapor_turu: Rapor türü
            veri: Dışa aktarılacak veri
            disari_aktar_dto: Dışa aktarım parametreleri
            
        Returns:
            str: Oluşturulan dosyanın tam yolu
            
        Raises:
            DosyaIslemHatasi: Dışa aktarım hatası
        """
        try:
            # Veriyi dict listesine çevir
            if isinstance(veri, list):
                if veri and hasattr(veri[0], '__dict__'):
                    # DTO listesi ise dict'e çevir
                    veri_dict_listesi = [
                        {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
                        for item in veri
                    ]
                else:
                    # Zaten dict listesi
                    veri_dict_listesi = veri
            else:
                # Tek nesne ise listeye çevir
                if hasattr(veri, '__dict__'):
                    veri_dict_listesi = [{k: v for k, v in veri.__dict__.items() if not k.startswith('_')}]
                else:
                    veri_dict_listesi = [veri]
            
            # Dışa aktarımı gerçekleştir
            return disari_aktar(rapor_turu, veri_dict_listesi, disari_aktar_dto)
            
        except DosyaIslemHatasi:
            raise
        except Exception as e:
            hata_mesaji = HataMesajlari.BEKLENMEYEN_HATA.format(str(e))
            self.logger.error(hata_mesaji)
            raise DosyaIslemHatasi(hata_mesaji)