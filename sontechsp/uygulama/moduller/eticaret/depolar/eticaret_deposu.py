# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.depolar.eticaret_deposu
# Description: E-ticaret hesapları ve siparişleri için repository sınıfı
# Changelog:
# - İlk oluşturma
# - EticaretDeposu CRUD operasyonları eklendi

"""
E-ticaret hesapları ve siparişleri için repository sınıfı.
Mağaza hesapları ve sipariş yönetimi işlemlerini sağlar.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ....veritabani.modeller.eticaret import EticaretHesaplari, EticaretSiparisleri
from ..dto import MagazaHesabiOlusturDTO, MagazaHesabiGuncelleDTO, SiparisDTO
from ..hatalar import EntegrasyonHatasi, VeriDogrulamaHatasi
from ..sifreleme import kimlik_sifrele, kimlik_sifreyi_coz

logger = logging.getLogger(__name__)


class EticaretDeposu:
    """
    E-ticaret hesapları ve siparişleri için repository sınıfı.
    
    Mağaza hesapları CRUD operasyonları:
    - Hesap oluşturma, güncelleme, listeleme
    - Hesap aktivasyon/deaktivasyon
    
    Sipariş operasyonları:
    - Sipariş kaydetme (duplicate kontrolü ile)
    - Sipariş sorgulama ve filtreleme
    - Sipariş durum güncelleme
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # Mağaza Hesabı Operasyonları
    
    def magaza_hesabi_ekle(self, hesap_dto: MagazaHesabiOlusturDTO) -> int:
        """
        Yeni mağaza hesabı ekler
        
        Args:
            hesap_dto: Mağaza hesabı bilgileri
            
        Returns:
            Oluşturulan hesabın ID'si
            
        Raises:
            VeriDogrulamaHatasi: Geçersiz veri durumunda
            EntegrasyonHatasi: Veritabanı hatası durumunda
        """
        try:
            # Kimlik bilgilerini şifrele
            sifreli_kimlik = kimlik_sifrele(hesap_dto.kimlik_json)
            
            hesap = EticaretHesaplari(
                platform=hesap_dto.platform,
                magaza_adi=hesap_dto.magaza_adi,
                aktif_mi=hesap_dto.aktif_mi,
                kimlik_json=sifreli_kimlik,
                ayar_json=hesap_dto.ayar_json
            )
            
            self.db.add(hesap)
            self.db.flush()  # ID'yi almak için
            
            logger.info(f"Mağaza hesabı eklendi - ID: {hesap.id}, "
                       f"Platform: {hesap_dto.platform}, Mağaza: {hesap_dto.magaza_adi}")
            
            return hesap.id
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Mağaza hesabı ekleme hatası - Integrity: {str(e)}")
            raise VeriDogrulamaHatasi(
                "Mağaza hesabı eklenemedi - veri kısıtlaması ihlali",
                detay=str(e)
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Mağaza hesabı ekleme hatası - DB: {str(e)}")
            raise EntegrasyonHatasi(
                "Mağaza hesabı eklenemedi - veritabanı hatası",
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
            
        Raises:
            EntegrasyonHatasi: Hesap bulunamadığında veya veritabanı hatası
        """
        try:
            hesap = self.db.query(EticaretHesaplari).filter(
                EticaretHesaplari.id == hesap_id
            ).first()
            
            if not hesap:
                raise EntegrasyonHatasi(f"Mağaza hesabı bulunamadı - ID: {hesap_id}")
            
            # Sadece None olmayan alanları güncelle
            if guncelleme_dto.magaza_adi is not None:
                hesap.magaza_adi = guncelleme_dto.magaza_adi
            if guncelleme_dto.kimlik_json is not None:
                # Kimlik bilgilerini şifrele
                hesap.kimlik_json = kimlik_sifrele(guncelleme_dto.kimlik_json)
            if guncelleme_dto.ayar_json is not None:
                hesap.ayar_json = guncelleme_dto.ayar_json
            if guncelleme_dto.aktif_mi is not None:
                hesap.aktif_mi = guncelleme_dto.aktif_mi
            
            hesap.guncelleme_zamani = datetime.now()
            
            logger.info(f"Mağaza hesabı güncellendi - ID: {hesap_id}")
            return True
            
        except SQLAlchemyError as e:
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
            platform: Platform filtresi (opsiyonel)
            aktif_mi: Aktiflik filtresi (opsiyonel)
            
        Returns:
            Mağaza hesapları listesi
        """
        try:
            query = self.db.query(EticaretHesaplari)
            
            if platform:
                query = query.filter(EticaretHesaplari.platform == platform)
            if aktif_mi is not None:
                query = query.filter(EticaretHesaplari.aktif_mi == aktif_mi)
            
            hesaplar = query.order_by(EticaretHesaplari.olusturma_zamani.desc()).all()
            
            logger.debug(f"Mağaza hesapları listelendi - Adet: {len(hesaplar)}, "
                        f"Platform: {platform}, Aktif: {aktif_mi}")
            
            return hesaplar
            
        except SQLAlchemyError as e:
            logger.error(f"Mağaza hesapları listeleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Mağaza hesapları listelenemedi",
                detay=str(e)
            )
    
    def magaza_hesabi_getir(self, hesap_id: int, kimlik_coz: bool = True) -> Optional[EticaretHesaplari]:
        """
        ID'ye göre mağaza hesabını getirir
        
        Args:
            hesap_id: Hesap ID'si
            kimlik_coz: Kimlik bilgilerini çöz (varsayılan True)
            
        Returns:
            Mağaza hesabı veya None
        """
        try:
            hesap = self.db.query(EticaretHesaplari).filter(
                EticaretHesaplari.id == hesap_id
            ).first()
            
            if hesap and kimlik_coz:
                # Kimlik bilgilerini çöz
                try:
                    hesap.kimlik_json = kimlik_sifreyi_coz(hesap.kimlik_json)
                except Exception as e:
                    logger.warning(f"Kimlik şifresi çözülemedi - ID: {hesap_id}, Hata: {str(e)}")
            
            return hesap
            
        except SQLAlchemyError as e:
            logger.error(f"Mağaza hesabı getirme hatası - ID: {hesap_id}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"Mağaza hesabı getirilemedi - ID: {hesap_id}",
                detay=str(e)
            )
    
    # Sipariş Operasyonları
    
    def siparis_kaydet(self, siparis_dto: SiparisDTO) -> int:
        """
        Sipariş kaydeder (duplicate kontrolü ile)
        
        Args:
            siparis_dto: Sipariş bilgileri
            
        Returns:
            Kaydedilen siparişin ID'si
            
        Raises:
            VeriDogrulamaHatasi: Duplicate sipariş durumunda
            EntegrasyonHatasi: Veritabanı hatası durumunda
        """
        try:
            # Duplicate kontrolü
            mevcut_siparis = self.db.query(EticaretSiparisleri).filter(
                and_(
                    EticaretSiparisleri.magaza_hesabi_id == siparis_dto.magaza_hesabi_id,
                    EticaretSiparisleri.dis_siparis_no == siparis_dto.dis_siparis_no
                )
            ).first()
            
            if mevcut_siparis:
                logger.warning(f"Duplicate sipariş - Mağaza: {siparis_dto.magaza_hesabi_id}, "
                              f"Sipariş: {siparis_dto.dis_siparis_no}")
                return mevcut_siparis.id
            
            siparis = EticaretSiparisleri(
                magaza_hesabi_id=siparis_dto.magaza_hesabi_id,
                platform=siparis_dto.platform,
                dis_siparis_no=siparis_dto.dis_siparis_no,
                siparis_zamani=siparis_dto.siparis_zamani,
                musteri_ad_soyad=siparis_dto.musteri_ad_soyad,
                toplam_tutar=siparis_dto.toplam_tutar,
                para_birimi=siparis_dto.para_birimi,
                durum=siparis_dto.durum,
                kargo_tasiyici=siparis_dto.kargo_tasiyici,
                takip_no=siparis_dto.takip_no,
                ham_veri_json=siparis_dto.ham_veri_json
            )
            
            self.db.add(siparis)
            self.db.flush()
            
            logger.info(f"Sipariş kaydedildi - ID: {siparis.id}, "
                       f"Platform: {siparis_dto.platform}, Sipariş: {siparis_dto.dis_siparis_no}")
            
            return siparis.id
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Sipariş kaydetme hatası - Integrity: {str(e)}")
            raise VeriDogrulamaHatasi(
                "Sipariş kaydedilemedi - veri kısıtlaması ihlali",
                detay=str(e)
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Sipariş kaydetme hatası - DB: {str(e)}")
            raise EntegrasyonHatasi(
                "Sipariş kaydedilemedi - veritabanı hatası",
                detay=str(e)
            )
    
    def siparis_listele(self, magaza_hesabi_id: Optional[int] = None,
                       durum: Optional[str] = None,
                       platform: Optional[str] = None,
                       limit: int = 100,
                       offset: int = 0) -> List[EticaretSiparisleri]:
        """
        Siparişleri listeler (filtreleme ile)
        
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
            query = self.db.query(EticaretSiparisleri)
            
            if magaza_hesabi_id:
                query = query.filter(EticaretSiparisleri.magaza_hesabi_id == magaza_hesabi_id)
            if durum:
                query = query.filter(EticaretSiparisleri.durum == durum)
            if platform:
                query = query.filter(EticaretSiparisleri.platform == platform)
            
            siparisler = query.order_by(
                desc(EticaretSiparisleri.siparis_zamani)
            ).limit(limit).offset(offset).all()
            
            logger.debug(f"Siparişler listelendi - Adet: {len(siparisler)}, "
                        f"Mağaza: {magaza_hesabi_id}, Durum: {durum}")
            
            return siparisler
            
        except SQLAlchemyError as e:
            logger.error(f"Sipariş listeleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "Siparişler listelenemedi",
                detay=str(e)
            )
    
    def siparis_durum_guncelle(self, siparis_id: int, yeni_durum: str, 
                              takip_no: Optional[str] = None) -> bool:
        """
        Sipariş durumunu günceller
        
        Args:
            siparis_id: Sipariş ID'si
            yeni_durum: Yeni durum
            takip_no: Kargo takip numarası (opsiyonel)
            
        Returns:
            Güncelleme başarılı ise True
            
        Raises:
            EntegrasyonHatasi: Sipariş bulunamadığında veya veritabanı hatası
        """
        try:
            siparis = self.db.query(EticaretSiparisleri).filter(
                EticaretSiparisleri.id == siparis_id
            ).first()
            
            if not siparis:
                raise EntegrasyonHatasi(f"Sipariş bulunamadı - ID: {siparis_id}")
            
            siparis.durum = yeni_durum
            if takip_no:
                siparis.takip_no = takip_no
            siparis.guncelleme_zamani = datetime.now()
            
            logger.info(f"Sipariş durumu güncellendi - ID: {siparis_id}, "
                       f"Durum: {yeni_durum}, Takip: {takip_no}")
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Sipariş durum güncelleme hatası - ID: {siparis_id}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"Sipariş durumu güncellenemedi - ID: {siparis_id}",
                detay=str(e)
            )