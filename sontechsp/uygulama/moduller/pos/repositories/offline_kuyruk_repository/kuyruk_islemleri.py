# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.offline_kuyruk_repository.kuyruk_islemleri
# Description: Kuyruk temel işlemleri
# Changelog:
# - Refactoring: Ana dosyadan kuyruk işlemleri ayrıldı

"""
Kuyruk Temel İşlemleri

Bu modül offline kuyruk temel CRUD operasyonlarını yönetir.
Kuyruk ekleme, getirme, güncelleme işlemleri sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc

from sontechsp.uygulama.veritabani.baglanti import sqlite_session
from sontechsp.uygulama.moduller.pos.arayuzler import (
    IOfflineKuyrukRepository, IslemTuru, KuyrukDurum
)
from sontechsp.uygulama.moduller.pos.database.models.offline_kuyruk import (
    OfflineKuyruk, offline_kuyruk_validasyon,
    satis_kuyruk_verisi_olustur, iade_kuyruk_verisi_olustur, stok_dusumu_kuyruk_verisi_olustur
)
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class KuyrukIslemleri:
    """
    Kuyruk temel işlemleri sınıfı
    
    Offline kuyruk CRUD operasyonlarını yönetir.
    """
    
    def kuyruga_ekle(self, islem_turu: IslemTuru, veri: Dict[str, Any], 
                    terminal_id: int = None, kasiyer_id: int = None, 
                    oncelik: int = 1, notlar: Optional[str] = None) -> int:
        """
        Kuyruğa yeni işlem ekler
        
        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            oncelik: İşlem önceliği (1=yüksek, 5=düşük)
            notlar: İşlem notları (opsiyonel)
            
        Returns:
            Oluşturulan kuyruk ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if terminal_id <= 0:
            raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
        
        if kasiyer_id <= 0:
            raise DogrulamaHatasi("Kasiyer ID pozitif olmalıdır")
        
        if not veri:
            raise DogrulamaHatasi("İşlem verisi boş olamaz")
        
        if oncelik < 1 or oncelik > 5:
            raise DogrulamaHatasi("Öncelik 1-5 arasında olmalıdır")
        
        with sqlite_session() as session:
            try:
                # Yeni kuyruk kaydı oluştur
                yeni_kuyruk = OfflineKuyruk(
                    islem_turu=islem_turu,
                    durum=KuyrukDurum.BEKLEMEDE,
                    veri=veri,
                    terminal_id=terminal_id,
                    kasiyer_id=kasiyer_id,
                    islem_tarihi=datetime.now(),
                    deneme_sayisi=0,
                    max_deneme_sayisi=3,
                    oncelik=oncelik,
                    notlar=notlar
                )
                
                # Validasyon
                hatalar = offline_kuyruk_validasyon(yeni_kuyruk)
                if hatalar:
                    raise DogrulamaHatasi(f"Kuyruk validasyon hataları: {', '.join(hatalar)}")
                
                session.add(yeni_kuyruk)
                session.commit()
                
                return yeni_kuyruk.id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Kuyruk ekleme hatası: {str(e)}")
    
    def kuyruk_ekle(self, islem_turu: IslemTuru, veri: Dict[str, Any], 
                   terminal_id: int, kasiyer_id: int, 
                   oncelik: int = 1, notlar: Optional[str] = None) -> int:
        """
        Kuyruğa yeni işlem ekler (alternatif metod adı)
        
        Args:
            islem_turu: İşlem türü
            veri: İşlem verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            oncelik: İşlem önceliği (1=yüksek, 5=düşük)
            notlar: İşlem notları (opsiyonel)
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        return self.kuyruga_ekle(islem_turu, veri, terminal_id, kasiyer_id, oncelik, notlar)
    
    def kuyruk_getir(self, kuyruk_id: int) -> Optional[Dict[str, Any]]:
        """
        Kuyruk kaydını getirir
        
        Args:
            kuyruk_id: Kuyruk kimliği
            
        Returns:
            Kuyruk bilgileri dict formatında veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz kuyruk ID
            VeritabaniHatasi: Veritabanı hatası
        """
        if kuyruk_id <= 0:
            raise DogrulamaHatasi("Kuyruk ID pozitif olmalıdır")
        
        with sqlite_session() as session:
            try:
                kuyruk = session.query(OfflineKuyruk).filter(OfflineKuyruk.id == kuyruk_id).first()
                
                if not kuyruk:
                    return None
                
                return self._kuyruk_dict_donustur(kuyruk)
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Kuyruk getirme hatası: {str(e)}")
    
    def satis_kuyruk_ekle(self, satis_data: Dict[str, Any], terminal_id: int, 
                         kasiyer_id: int) -> int:
        """
        Satış işlemi için kuyruk ekler
        
        Args:
            satis_data: Satış verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        veri = satis_kuyruk_verisi_olustur(satis_data)
        return self.kuyruk_ekle(IslemTuru.SATIS, veri, terminal_id, kasiyer_id, oncelik=1)
    
    def iade_kuyruk_ekle(self, iade_data: Dict[str, Any], terminal_id: int, 
                        kasiyer_id: int) -> int:
        """
        İade işlemi için kuyruk ekler
        
        Args:
            iade_data: İade verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        veri = iade_kuyruk_verisi_olustur(iade_data)
        return self.kuyruk_ekle(IslemTuru.IADE, veri, terminal_id, kasiyer_id, oncelik=2)
    
    def stok_dusumu_kuyruk_ekle(self, stok_data: Dict[str, Any], terminal_id: int, 
                               kasiyer_id: int) -> int:
        """
        Stok düşümü işlemi için kuyruk ekler
        
        Args:
            stok_data: Stok düşümü verisi
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Oluşturulan kuyruk ID'si
        """
        veri = stok_dusumu_kuyruk_verisi_olustur(stok_data)
        return self.kuyruk_ekle(IslemTuru.STOK_DUSUMU, veri, terminal_id, kasiyer_id, oncelik=3)
    
    def _kuyruk_dict_donustur(self, kuyruk: OfflineKuyruk) -> Dict[str, Any]:
        """
        OfflineKuyruk nesnesini dict formatına çevirir (private method)
        
        Args:
            kuyruk: OfflineKuyruk nesnesi
            
        Returns:
            Dict formatında kuyruk bilgileri
        """
        return {
            'id': kuyruk.id,
            'islem_turu': kuyruk.islem_turu.value,
            'durum': kuyruk.durum.value,
            'veri': kuyruk.veri,
            'terminal_id': kuyruk.terminal_id,
            'kasiyer_id': kuyruk.kasiyer_id,
            'islem_tarihi': kuyruk.islem_tarihi.isoformat(),
            'son_deneme_tarihi': kuyruk.son_deneme_tarihi.isoformat() if kuyruk.son_deneme_tarihi else None,
            'tamamlanma_tarihi': kuyruk.tamamlanma_tarihi.isoformat() if kuyruk.tamamlanma_tarihi else None,
            'deneme_sayisi': kuyruk.deneme_sayisi,
            'max_deneme_sayisi': kuyruk.max_deneme_sayisi,
            'hata_mesaji': kuyruk.hata_mesaji,
            'oncelik': kuyruk.oncelik,
            'notlar': kuyruk.notlar,
            'olusturma_tarihi': kuyruk.olusturma_tarihi.isoformat() if kuyruk.olusturma_tarihi else None,
            'guncelleme_tarihi': kuyruk.guncelleme_tarihi.isoformat() if kuyruk.guncelleme_tarihi else None,
            # Hesaplanan alanlar
            'beklemede_mi': kuyruk.beklemede_mi(),
            'isleniyor_mu': kuyruk.isleniyor_mu(),
            'tamamlandi_mi': kuyruk.tamamlandi_mi(),
            'hata_durumunda_mi': kuyruk.hata_durumunda_mi(),
            'tekrar_denenebilir_mi': kuyruk.tekrar_denenebilir_mi(),
            'max_deneme_asildi_mi': kuyruk.max_deneme_asildi_mi(),
            'gecikme_suresi_saniye': kuyruk.gecikme_suresi_hesapla()
        }