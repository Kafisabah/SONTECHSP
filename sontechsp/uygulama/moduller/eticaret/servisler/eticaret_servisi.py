# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.servisler.eticaret_servisi
# Description: E-ticaret entegrasyonu ana servis sınıfı
# Changelog:
# - İlk oluşturma
# - EticaretServisi iş mantığı eklendi

"""
E-ticaret entegrasyonu ana servis sınıfı.
Mağaza hesapları ve sipariş yönetimi iş mantığını sağlar.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..depolar import EticaretDeposu, JobDeposu
from ..baglanti_fabrikasi import BaglantiFabrikasi
from ..dto import (
    MagazaHesabiOlusturDTO, MagazaHesabiGuncelleDTO, SiparisDTO,
    JobDTO, JobSonucDTO
)
from ..sabitler import JobTurleri, JobDurumlari, SiparisDurumlari
from ..hatalar import EntegrasyonHatasi, VeriDogrulamaHatasi, PlatformHatasi
from ..dogrulama import siparis_durum_gecisini_dogrula
from ....veritabani.modeller.eticaret import EticaretHesaplari, EticaretSiparisleri

logger = logging.getLogger(__name__)


class EticaretServisi:
    """
    E-ticaret entegrasyonu ana servis sınıfı.
    
    İş mantığı operasyonları:
    - Mağaza hesabı yönetimi
    - Sipariş senkronizasyonu
    - Platform entegrasyonu
    - Transaction yönetimi
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.eticaret_deposu = EticaretDeposu(db_session)
        self.job_deposu = JobDeposu(db_session)
    
    # Mağaza Hesabı Yönetimi
    
    def magaza_hesabi_olustur(self, hesap_dto: MagazaHesabiOlusturDTO) -> int:
        """
        Yeni mağaza hesabı oluşturur
        
        Args:
            hesap_dto: Mağaza hesabı bilgileri
            
        Returns:
            Oluşturulan hesabın ID'si
            
        Raises:
            VeriDogrulamaHatasi: Geçersiz veri durumunda
            EntegrasyonHatasi: İşlem hatası durumunda
        """
        try:
            # DTO validasyonu (zaten __post_init__'te yapılıyor)
            logger.info(f"Mağaza hesabı oluşturuluyor - Platform: {hesap_dto.platform}, "
                       f"Mağaza: {hesap_dto.magaza_adi}")
            
            # Transaction başlat
            hesap_id = self.eticaret_deposu.magaza_hesabi_ekle(hesap_dto)
            
            # Bağlantı testi (opsiyonel)
            if hesap_dto.aktif_mi:
                try:
                    self._baglanti_test_et(hesap_id)
                    logger.info(f"Mağaza hesabı bağlantı testi başarılı - ID: {hesap_id}")
                except Exception as e:
                    logger.warning(f"Mağaza hesabı bağlantı testi başarısız - ID: {hesap_id}, "
                                  f"Hata: {str(e)}")
            
            self.db.commit()
            
            logger.info(f"Mağaza hesabı başarıyla oluşturuldu - ID: {hesap_id}")
            return hesap_id
            
        except (VeriDogrulamaHatasi, EntegrasyonHatasi):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Mağaza hesabı oluşturma hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Mağaza hesabı oluşturulamadı",
                detay=str(e)
            )
    
    def magaza_hesabi_guncelle(self, hesap_id: int, guncelleme_dto: MagazaHesabiGuncelleDTO) -> bool:
        """
        Mağaza hesabını günceller
        
        Args:
            hesap_id: Hesap ID'si
            guncelleme_dto: Güncelleme bilgileri
            
        Returns:
            Güncelleme başarılı ise True
        """
        try:
            logger.info(f"Mağaza hesabı güncelleniyor - ID: {hesap_id}")
            
            # Transaction başlat
            sonuc = self.eticaret_deposu.magaza_hesabi_guncelle(hesap_id, guncelleme_dto)
            
            # Aktiflik değişti ise bağlantı testi
            if guncelleme_dto.aktif_mi is True:
                try:
                    self._baglanti_test_et(hesap_id)
                    logger.info(f"Güncellenen hesap bağlantı testi başarılı - ID: {hesap_id}")
                except Exception as e:
                    logger.warning(f"Güncellenen hesap bağlantı testi başarısız - ID: {hesap_id}, "
                                  f"Hata: {str(e)}")
            
            self.db.commit()
            
            logger.info(f"Mağaza hesabı başarıyla güncellendi - ID: {hesap_id}")
            return sonuc
            
        except EntegrasyonHatasi:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Mağaza hesabı güncelleme hatası - ID: {hesap_id}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"Mağaza hesabı güncellenemedi - ID: {hesap_id}",
                detay=str(e)
            )
    
    def magaza_hesabi_listele(self, platform: Optional[str] = None, 
                             aktif_mi: Optional[bool] = None) -> List[EticaretHesaplari]:
        """
        Mağaza hesaplarını listeler
        
        Args:
            platform: Platform filtresi
            aktif_mi: Aktiflik filtresi
            
        Returns:
            Mağaza hesapları listesi
        """
        try:
            return self.eticaret_deposu.magaza_hesabi_listele(platform, aktif_mi)
        except Exception as e:
            logger.error(f"Mağaza hesapları listeleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Mağaza hesapları listelenemedi",
                detay=str(e)
            )
    
    def magaza_hesabi_getir(self, hesap_id: int) -> Optional[EticaretHesaplari]:
        """
        Mağaza hesabını getirir
        
        Args:
            hesap_id: Hesap ID'si
            
        Returns:
            Mağaza hesabı veya None
        """
        try:
            return self.eticaret_deposu.magaza_hesabi_getir(hesap_id)
        except Exception as e:
            logger.error(f"Mağaza hesabı getirme hatası - ID: {hesap_id}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"Mağaza hesabı getirilemedi - ID: {hesap_id}",
                detay=str(e)
            )
    
    # Sipariş Yönetimi
    
    def siparis_senkronize_et(self, magaza_hesabi_id: int, 
                             sonra: Optional[datetime] = None) -> int:
        """
        Mağaza siparişlerini senkronize eder
        
        Args:
            magaza_hesabi_id: Mağaza hesabı ID'si
            sonra: Bu tarihten sonraki siparişleri getir
            
        Returns:
            Senkronize edilen sipariş sayısı
        """
        try:
            logger.info(f"Sipariş senkronizasyonu başlatılıyor - Mağaza: {magaza_hesabi_id}")
            
            # Mağaza hesabını getir
            hesap = self.eticaret_deposu.magaza_hesabi_getir(magaza_hesabi_id)
            if not hesap:
                raise EntegrasyonHatasi(f"Mağaza hesabı bulunamadı - ID: {magaza_hesabi_id}")
            
            if not hesap.aktif_mi:
                raise EntegrasyonHatasi(f"Mağaza hesabı aktif değil - ID: {magaza_hesabi_id}")
            
            # Bağlayıcı oluştur
            baglayici = BaglantiFabrikasi.baglayici_olustur(
                hesap.platform,
                hesap.id,
                hesap.kimlik_json,
                hesap.ayar_json
            )
            
            # Siparişleri çek
            siparisler = baglayici.siparisleri_cek(sonra)
            
            # Siparişleri kaydet
            kaydedilen_sayi = 0
            for siparis_dto in siparisler:
                try:
                    self.eticaret_deposu.siparis_kaydet(siparis_dto)
                    kaydedilen_sayi += 1
                except Exception as e:
                    logger.warning(f"Sipariş kaydedilemedi - Sipariş: {siparis_dto.dis_siparis_no}, "
                                  f"Hata: {str(e)}")
            
            self.db.commit()
            
            logger.info(f"Sipariş senkronizasyonu tamamlandı - Mağaza: {magaza_hesabi_id}, "
                       f"Toplam: {len(siparisler)}, Kaydedilen: {kaydedilen_sayi}")
            
            return kaydedilen_sayi
            
        except EntegrasyonHatasi:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Sipariş senkronizasyon hatası - Mağaza: {magaza_hesabi_id}, "
                        f"Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"Sipariş senkronizasyonu başarısız - Mağaza: {magaza_hesabi_id}",
                detay=str(e)
            )
    
    def siparis_listele(self, magaza_hesabi_id: Optional[int] = None,
                       durum: Optional[str] = None,
                       platform: Optional[str] = None,
                       limit: int = 100,
                       offset: int = 0) -> List[EticaretSiparisleri]:
        """
        Siparişleri listeler
        
        Args:
            magaza_hesabi_id: Mağaza hesabı filtresi
            durum: Durum filtresi
            platform: Platform filtresi
            limit: Maksimum kayıt sayısı
            offset: Başlangıç offset'i
            
        Returns:
            Sipariş listesi
        """
        try:
            return self.eticaret_deposu.siparis_listele(
                magaza_hesabi_id, durum, platform, limit, offset
            )
        except Exception as e:
            logger.error(f"Sipariş listeleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Siparişler listelenemedi",
                detay=str(e)
            )
    
    def siparis_durum_guncelle(self, siparis_id: int, yeni_durum: str, 
                              takip_no: Optional[str] = None,
                              platforma_gonder: bool = True) -> bool:
        """
        Sipariş durumunu günceller
        
        Args:
            siparis_id: Sipariş ID'si
            yeni_durum: Yeni durum
            takip_no: Kargo takip numarası
            platforma_gonder: Platforma da gönder
            
        Returns:
            Güncelleme başarılı ise True
        """
        try:
            logger.info(f"Sipariş durumu güncelleniyor - ID: {siparis_id}, "
                       f"Durum: {yeni_durum}")
            
            # Durum validasyonu
            if yeni_durum not in [d.value for d in SiparisDurumlari]:
                raise VeriDogrulamaHatasi(f"Geçersiz sipariş durumu: {yeni_durum}")
            
            # Mevcut durumu kontrol et ve geçiş doğrulaması yap
            siparis = self.db.query(EticaretSiparisleri).filter(
                EticaretSiparisleri.id == siparis_id
            ).first()
            
            if siparis:
                try:
                    siparis_durum_gecisini_dogrula(siparis.durum, yeni_durum)
                except VeriDogrulamaHatasi as e:
                    raise VeriDogrulamaHatasi(f"Durum geçiş hatası: {e.mesaj}")
            
            # Sipariş güncelle
            sonuc = self.eticaret_deposu.siparis_durum_guncelle(siparis_id, yeni_durum, takip_no)
            
            # Platforma gönder (opsiyonel)
            if platforma_gonder and sonuc:
                try:
                    self._siparis_durum_platforma_gonder(siparis_id, yeni_durum, takip_no)
                except Exception as e:
                    logger.warning(f"Sipariş durumu platforma gönderilemedi - ID: {siparis_id}, "
                                  f"Hata: {str(e)}")
            
            self.db.commit()
            
            logger.info(f"Sipariş durumu başarıyla güncellendi - ID: {siparis_id}")
            return sonuc
            
        except (VeriDogrulamaHatasi, EntegrasyonHatasi):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Sipariş durum güncelleme hatası - ID: {siparis_id}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"Sipariş durumu güncellenemedi - ID: {siparis_id}",
                detay=str(e)
            )
    
    # Yardımcı Metodlar
    
    def _baglanti_test_et(self, hesap_id: int) -> bool:
        """
        Mağaza hesabı bağlantısını test eder
        
        Args:
            hesap_id: Hesap ID'si
            
        Returns:
            Bağlantı başarılı ise True
            
        Raises:
            PlatformHatasi: Bağlantı hatası durumunda
        """
        hesap = self.eticaret_deposu.magaza_hesabi_getir(hesap_id)
        if not hesap:
            raise EntegrasyonHatasi(f"Mağaza hesabı bulunamadı - ID: {hesap_id}")
        
        try:
            baglayici = BaglantiFabrikasi.baglayici_olustur(
                hesap.platform,
                hesap.id,
                hesap.kimlik_json,
                hesap.ayar_json
            )
            
            return baglayici.test_baglanti()
            
        except Exception as e:
            raise PlatformHatasi(
                "Platform bağlantı testi başarısız",
                platform=hesap.platform,
                detay=str(e)
            )
    
    def _siparis_durum_platforma_gonder(self, siparis_id: int, yeni_durum: str, 
                                       takip_no: Optional[str] = None) -> None:
        """
        Sipariş durum güncellemesini platforma gönderir
        
        Args:
            siparis_id: Sipariş ID'si
            yeni_durum: Yeni durum
            takip_no: Takip numarası
        """
        # Sipariş bilgilerini getir
        siparis = self.db.query(EticaretSiparisleri).filter(
            EticaretSiparisleri.id == siparis_id
        ).first()
        
        if not siparis:
            raise EntegrasyonHatasi(f"Sipariş bulunamadı - ID: {siparis_id}")
        
        # Mağaza hesabını getir
        hesap = self.eticaret_deposu.magaza_hesabi_getir(siparis.magaza_hesabi_id)
        if not hesap or not hesap.aktif_mi:
            raise EntegrasyonHatasi(f"Mağaza hesabı aktif değil - ID: {siparis.magaza_hesabi_id}")
        
        # Bağlayıcı oluştur ve gönder
        baglayici = BaglantiFabrikasi.baglayici_olustur(
            hesap.platform,
            hesap.id,
            hesap.kimlik_json,
            hesap.ayar_json
        )
        
        baglayici.siparis_durum_guncelle(siparis.dis_siparis_no, yeni_durum, takip_no)