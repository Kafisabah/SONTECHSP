# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.satis_repository.satis_sorgular
# Description: Satış sorgu işlemleri
# Changelog:
# - Refactoring: Ana dosyadan sorgu işlemleri ayrıldı

"""
Satış Sorgu İşlemleri

Bu modül karmaşık satış sorgularını ve listeleme işlemlerini yönetir.
Filtreleme, arama ve özel sorgu operasyonları sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.arayuzler import SatisDurum, OdemeTuru
from sontechsp.uygulama.moduller.pos.database.models.satis import (
    Satis, SatisOdeme, satis_odeme_validasyon
)
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class SatisSorgular:
    """
    Satış sorgu işlemleri sınıfı
    
    Karmaşık sorgular ve listeleme operasyonlarını yönetir.
    """
    
    def satis_listesi_getir(self, terminal_id: Optional[int] = None, 
                          kasiyer_id: Optional[int] = None,
                          baslangic_tarihi: Optional[datetime] = None,
                          bitis_tarihi: Optional[datetime] = None,
                          durum: Optional[SatisDurum] = None,
                          limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Satış listesini getirir
        
        Args:
            terminal_id: Terminal kimliği (opsiyonel)
            kasiyer_id: Kasiyer kimliği (opsiyonel)
            baslangic_tarihi: Başlangıç tarihi (opsiyonel)
            bitis_tarihi: Bitiş tarihi (opsiyonel)
            durum: Satış durumu (opsiyonel)
            limit: Maksimum kayıt sayısı
            offset: Başlangıç offset'i
            
        Returns:
            Satış listesi
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if limit <= 0 or limit > 1000:
            raise DogrulamaHatasi("Limit 1-1000 arasında olmalıdır")
        
        if offset < 0:
            raise DogrulamaHatasi("Offset negatif olamaz")
        
        with postgresql_session() as session:
            try:
                query = session.query(Satis).options(joinedload(Satis.odemeler))
                
                # Filtreleri uygula
                if terminal_id:
                    query = query.filter(Satis.terminal_id == terminal_id)
                
                if kasiyer_id:
                    query = query.filter(Satis.kasiyer_id == kasiyer_id)
                
                if baslangic_tarihi:
                    query = query.filter(Satis.satis_tarihi >= baslangic_tarihi)
                
                if bitis_tarihi:
                    query = query.filter(Satis.satis_tarihi <= bitis_tarihi)
                
                if durum:
                    query = query.filter(Satis.durum == durum)
                
                # Sıralama ve sayfalama
                query = query.order_by(desc(Satis.satis_tarihi))
                query = query.offset(offset).limit(limit)
                
                satislar = query.all()
                
                # Dict formatına çevir
                sonuc = []
                for satis in satislar:
                    satis_dict = {
                        'id': satis.id,
                        'sepet_id': satis.sepet_id,
                        'terminal_id': satis.terminal_id,
                        'kasiyer_id': satis.kasiyer_id,
                        'satis_tarihi': satis.satis_tarihi.isoformat(),
                        'toplam_tutar': float(satis.toplam_tutar),
                        'indirim_tutari': float(satis.indirim_tutari),
                        'net_tutar': float(satis.net_tutar_hesapla()),
                        'durum': satis.durum.value,
                        'fis_no': satis.fis_no,
                        'musteri_id': satis.musteri_id,
                        'toplam_odeme_tutari': float(satis.toplam_odeme_tutari()),
                        'odeme_tamamlandi': satis.odeme_tamamlandi_mi()
                    }
                    sonuc.append(satis_dict)
                
                return sonuc
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Satış listesi getirme hatası: {str(e)}")
    
    def fis_no_ile_satis_getir(self, fis_no: str) -> Optional[Dict[str, Any]]:
        """
        Fiş numarası ile satış getirir
        
        Args:
            fis_no: Fiş numarası
            
        Returns:
            Satış bilgileri veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz fiş numarası
            VeritabaniHatasi: Veritabanı hatası
        """
        if not fis_no or not fis_no.strip():
            raise DogrulamaHatasi("Fiş numarası boş olamaz")
        
        with postgresql_session() as session:
            try:
                satis = session.query(Satis).options(
                    joinedload(Satis.odemeler)
                ).filter(Satis.fis_no == fis_no.strip()).first()
                
                if not satis:
                    return None
                
                return self.satis_getir(satis.id)
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Fiş ile satış getirme hatası: {str(e)}")
    
    def sepet_ile_satis_getir(self, sepet_id: int) -> Optional[Dict[str, Any]]:
        """
        Sepet ID ile satış getirir
        
        Args:
            sepet_id: Sepet kimliği
            
        Returns:
            Satış bilgileri veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz sepet ID
            VeritabaniHatasi: Veritabanı hatası
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")
        
        try:
            with postgresql_session() as session:
                satis = session.query(Satis).options(
                    joinedload(Satis.odemeler)
                ).filter(Satis.sepet_id == sepet_id).first()
                
                if not satis:
                    return None
                
                return {
                    'id': satis.id,
                    'sepet_id': satis.sepet_id,
                    'terminal_id': satis.terminal_id,
                    'kasiyer_id': satis.kasiyer_id,
                    'satis_tarihi': satis.satis_tarihi.isoformat(),
                    'toplam_tutar': float(satis.toplam_tutar),
                    'indirim_tutari': float(satis.indirim_tutari or 0),
                    'durum': satis.durum,
                    'fis_no': satis.fis_no,
                    'musteri_id': satis.musteri_id,
                    'notlar': satis.notlar,
                    'odemeler': [
                        {
                            'id': odeme.id,
                            'odeme_turu': odeme.odeme_turu,
                            'tutar': float(odeme.tutar),
                            'referans_no': odeme.referans_no,
                            'kart_son_4_hane': odeme.kart_son_4_hane,
                            'banka_kodu': odeme.banka_kodu,
                            'taksit_sayisi': odeme.taksit_sayisi,
                            'odeme_tarihi': odeme.odeme_tarihi.isoformat()
                        }
                        for odeme in satis.odemeler
                    ]
                }
                
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Sepet ile satış getirme hatası: {str(e)}")
    
    def odeme_ekle(self, satis_id: int, odeme_turu: OdemeTuru, tutar: Decimal,
                  referans_no: Optional[str] = None, kart_son_4_hane: Optional[str] = None,
                  banka_kodu: Optional[str] = None, taksit_sayisi: Optional[int] = None) -> int:
        """
        Satışa ödeme ekler
        
        Args:
            satis_id: Satış kimliği
            odeme_turu: Ödeme türü
            tutar: Ödeme tutarı
            referans_no: Referans numarası (opsiyonel)
            kart_son_4_hane: Kart son 4 hanesi (opsiyonel)
            banka_kodu: Banka kodu (opsiyonel)
            taksit_sayisi: Taksit sayısı (opsiyonel)
            
        Returns:
            Oluşturulan ödeme ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Satış bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if satis_id <= 0:
            raise DogrulamaHatasi("Satış ID pozitif olmalıdır")
        
        if tutar <= 0:
            raise DogrulamaHatasi("Ödeme tutarı pozitif olmalıdır")
        
        if taksit_sayisi and taksit_sayisi <= 0:
            raise DogrulamaHatasi("Taksit sayısı pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                # Satış var mı kontrol et
                satis = session.query(Satis).filter(Satis.id == satis_id).first()
                if not satis:
                    raise SontechHatasi(f"Satış bulunamadı: {satis_id}")
                
                # Yeni ödeme oluştur
                yeni_odeme = SatisOdeme(
                    satis_id=satis_id,
                    odeme_turu=odeme_turu,
                    tutar=tutar,
                    referans_no=referans_no,
                    odeme_tarihi=datetime.now(),
                    kart_son_4_hane=kart_son_4_hane,
                    banka_kodu=banka_kodu,
                    taksit_sayisi=taksit_sayisi or 1
                )
                
                # Validasyon
                hatalar = satis_odeme_validasyon(yeni_odeme)
                if hatalar:
                    raise DogrulamaHatasi(f"Ödeme validasyon hataları: {', '.join(hatalar)}")
                
                session.add(yeni_odeme)
                session.commit()
                
                return yeni_odeme.id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Ödeme ekleme hatası: {str(e)}")
    
    def satis_odeme_ekle(self, satis_id: int, odeme_turu: OdemeTuru, 
                        tutar: Decimal, referans_no: str = None) -> int:
        """
        Satışa ödeme ekler
        
        Args:
            satis_id: Satış kimliği
            odeme_turu: Ödeme türü
            tutar: Ödeme tutarı
            referans_no: Referans numarası (opsiyonel)
            
        Returns:
            Ödeme kimliği
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with postgresql_session() as session:
                # Satış kaydını kontrol et
                satis = session.query(Satis).filter(Satis.id == satis_id).first()
                if not satis:
                    raise DogrulamaHatasi(f"Satış bulunamadı: {satis_id}")
                
                # Ödeme kaydı oluştur
                from sontechsp.uygulama.moduller.pos.database.models.satis import SatisOdeme
                
                odeme = SatisOdeme(
                    satis_id=satis_id,
                    odeme_turu=odeme_turu,
                    tutar=tutar,
                    referans_no=referans_no,
                    odeme_tarihi=datetime.now()
                )
                
                session.add(odeme)
                session.flush()
                
                odeme_id = odeme.id
                session.commit()
                
                return odeme_id
                
        except DogrulamaHatasi:
            raise
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Ödeme ekleme hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"Ödeme ekleme işlemi başarısız: {str(e)}")