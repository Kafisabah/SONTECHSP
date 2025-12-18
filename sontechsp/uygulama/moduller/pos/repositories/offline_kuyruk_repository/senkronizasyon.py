# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.offline_kuyruk_repository.senkronizasyon
# Description: Kuyruk senkronizasyon işlemleri
# Changelog:
# - Refactoring: Ana dosyadan senkronizasyon işlemleri ayrıldı

"""
Kuyruk Senkronizasyon İşlemleri

Bu modül offline kuyruk senkronizasyon ve durum yönetimi işlemlerini yönetir.
Kuyruk durumu güncelleme, deneme artırma ve listeleme işlemleri sağlar.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc

from sontechsp.uygulama.veritabani.baglanti import sqlite_session
from sontechsp.uygulama.moduller.pos.arayuzler import KuyrukDurum
from sontechsp.uygulama.moduller.pos.database.models.offline_kuyruk import (
    OfflineKuyruk, offline_kuyruk_validasyon
)
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class Senkronizasyon:
    """
    Kuyruk senkronizasyon işlemleri sınıfı
    
    Kuyruk durumu yönetimi ve senkronizasyon operasyonlarını yönetir.
    """
    
    def bekleyen_kuyruk_listesi(self, terminal_id: Optional[int] = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """
        Bekleyen kuyruk kayıtlarını getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            limit: Maksimum kayıt sayısı
            
        Returns:
            Bekleyen kuyruk listesi
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if limit <= 0 or limit > 1000:
            raise DogrulamaHatasi("Limit 1-1000 arasında olmalıdır")
        
        with sqlite_session() as session:
            try:
                query = session.query(OfflineKuyruk).filter(
                    OfflineKuyruk.durum == KuyrukDurum.BEKLEMEDE
                )
                
                if terminal_id:
                    query = query.filter(OfflineKuyruk.terminal_id == terminal_id)
                
                # Öncelik ve tarihe göre sırala
                query = query.order_by(
                    asc(OfflineKuyruk.oncelik),
                    asc(OfflineKuyruk.islem_tarihi)
                ).limit(limit)
                
                kuyruklar = query.all()
                
                return [self._kuyruk_dict_donustur(kuyruk) for kuyruk in kuyruklar]
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Bekleyen kuyruk listesi hatası: {str(e)}")
    
    def kuyruk_durum_guncelle(self, kuyruk_id: int, yeni_durum: KuyrukDurum,
                            hata_mesaji: Optional[str] = None) -> bool:
        """
        Kuyruk durumunu günceller
        
        Args:
            kuyruk_id: Kuyruk kimliği
            yeni_durum: Yeni durum
            hata_mesaji: Hata mesajı (hata durumu için)
            
        Returns:
            Güncelleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Kuyruk bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if kuyruk_id <= 0:
            raise DogrulamaHatasi("Kuyruk ID pozitif olmalıdır")
        
        with sqlite_session() as session:
            try:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                if not kuyruk:
                    raise SontechHatasi(f"Kuyruk bulunamadı: {kuyruk_id}")
                
                # Duruma göre güncelleme
                if yeni_durum == KuyrukDurum.ISLENIYOR:
                    kuyruk.isleme_basla()
                elif yeni_durum == KuyrukDurum.TAMAMLANDI:
                    kuyruk.tamamla()
                elif yeni_durum == KuyrukDurum.HATA:
                    kuyruk.hata_durumuna_getir(hata_mesaji or "Bilinmeyen hata")
                elif yeni_durum == KuyrukDurum.BEKLEMEDE:
                    kuyruk.beklemede_durumuna_getir()
                
                # Validasyon
                hatalar = offline_kuyruk_validasyon(kuyruk)
                if hatalar:
                    raise DogrulamaHatasi(f"Kuyruk validasyon hataları: {', '.join(hatalar)}")
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk durum güncelleme hatası: {str(e)}")
    
    def kuyruk_deneme_artir(self, kuyruk_id: int, hata_mesaji: str) -> bool:
        """
        Kuyruk deneme sayısını artırır
        
        Args:
            kuyruk_id: Kuyruk kimliği
            hata_mesaji: Hata mesajı
            
        Returns:
            Artırma başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Kuyruk bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if kuyruk_id <= 0:
            raise DogrulamaHatasi("Kuyruk ID pozitif olmalıdır")
        
        if not hata_mesaji or not hata_mesaji.strip():
            raise DogrulamaHatasi("Hata mesajı boş olamaz")
        
        with sqlite_session() as session:
            try:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                if not kuyruk:
                    raise SontechHatasi(f"Kuyruk bulunamadı: {kuyruk_id}")
                
                kuyruk.deneme_artir()
                
                # Maksimum deneme sayısı aşıldı mı kontrol et
                if kuyruk.max_deneme_asildi_mi():
                    kuyruk.hata_durumuna_getir(f"Maksimum deneme sayısı aşıldı: {hata_mesaji}")
                else:
                    kuyruk.hata_durumuna_getir(hata_mesaji)
                    kuyruk.beklemede_durumuna_getir()  # Tekrar deneme için
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk deneme artırma hatası: {str(e)}")
    
    def hata_durumundaki_kuyruklar(self, terminal_id: Optional[int] = None,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """
        Hata durumundaki kuyruk kayıtlarını getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            limit: Maksimum kayıt sayısı
            
        Returns:
            Hata durumundaki kuyruk listesi
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if limit <= 0 or limit > 1000:
            raise DogrulamaHatasi("Limit 1-1000 arasında olmalıdır")
        
        with sqlite_session() as session:
            try:
                query = session.query(OfflineKuyruk).filter(
                    OfflineKuyruk.durum == KuyrukDurum.HATA
                )
                
                if terminal_id:
                    query = query.filter(OfflineKuyruk.terminal_id == terminal_id)
                
                # Son deneme tarihine göre sırala
                query = query.order_by(desc(OfflineKuyruk.son_deneme_tarihi)).limit(limit)
                
                kuyruklar = query.all()
                
                return [self._kuyruk_dict_donustur(kuyruk) for kuyruk in kuyruklar]
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Hata durumundaki kuyruklar hatası: {str(e)}")
    
    def bekleyen_islemler(self) -> List[Dict[str, Any]]:
        """
        Bekleyen işlemleri getirir
        
        Returns:
            Bekleyen işlem listesi
            
        Raises:
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                kuyruklar = session.query(OfflineKuyruk).filter(
                    OfflineKuyruk.durum == KuyrukDurum.BEKLEMEDE
                ).order_by(OfflineKuyruk.oncelik, OfflineKuyruk.islem_tarihi).all()
                
                return [self._kuyruk_dict_donustur(kuyruk) for kuyruk in kuyruklar]
                
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Bekleyen işlemler getirme hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"Bekleyen işlemler getirme işlemi başarısız: {str(e)}")
    
    def islem_tamamla(self, kuyruk_id: int) -> bool:
        """
        İşlemi tamamlandı olarak işaretler
        
        Args:
            kuyruk_id: Kuyruk kimliği
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            DogrulamaHatasi: Geçersiz kuyruk kimliği
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                
                if not kuyruk:
                    raise DogrulamaHatasi(f"Kuyruk kaydı bulunamadı: {kuyruk_id}")
                
                kuyruk.durum = KuyrukDurum.TAMAMLANDI
                kuyruk.guncelleme_tarihi = datetime.now()
                
                session.commit()
                return True
                
        except DogrulamaHatasi:
            raise
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"İşlem tamamlama hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"İşlem tamamlama işlemi başarısız: {str(e)}")
    
    def islem_hata(self, kuyruk_id: int, hata_mesaji: str) -> bool:
        """
        İşlemi hatalı olarak işaretler
        
        Args:
            kuyruk_id: Kuyruk kimliği
            hata_mesaji: Hata mesajı
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            DogrulamaHatasi: Geçersiz kuyruk kimliği
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with sqlite_session() as session:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                
                if not kuyruk:
                    raise DogrulamaHatasi(f"Kuyruk kaydı bulunamadı: {kuyruk_id}")
                
                kuyruk.durum = KuyrukDurum.HATA
                kuyruk.hata_mesaji = hata_mesaji
                kuyruk.deneme_sayisi += 1
                kuyruk.guncelleme_tarihi = datetime.now()
                
                session.commit()
                return True
                
        except DogrulamaHatasi:
            raise
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"İşlem hata işaretleme hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"İşlem hata işaretleme işlemi başarısız: {str(e)}")