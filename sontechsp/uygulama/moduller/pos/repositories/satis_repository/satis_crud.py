# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.satis_repository.satis_crud
# Description: Satış CRUD işlemleri
# Changelog:
# - Refactoring: Ana dosyadan CRUD işlemleri ayrıldı

"""
Satış CRUD İşlemleri

Bu modül satış ve ödeme temel CRUD operasyonlarını yönetir.
Oluşturma, okuma, güncelleme ve silme işlemleri sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.arayuzler import ISatisRepository, SatisDurum, OdemeTuru
from sontechsp.uygulama.moduller.pos.database.models.satis import (
    Satis, SatisOdeme, satis_validasyon, satis_odeme_validasyon
)
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class SatisCrud:
    """
    Satış CRUD işlemleri sınıfı
    
    Temel satış ve ödeme CRUD operasyonlarını yönetir.
    """
    
    def satis_olustur(self, sepet_id: int, terminal_id: int, kasiyer_id: int,
                     toplam_tutar: Decimal, indirim_tutari: Optional[Decimal] = None,
                     musteri_id: Optional[int] = None, notlar: Optional[str] = None) -> int:
        """
        Yeni satış kaydı oluşturur
        
        Args:
            sepet_id: Sepet kimliği
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            toplam_tutar: Toplam tutar
            indirim_tutari: İndirim tutarı (opsiyonel)
            musteri_id: Müşteri kimliği (opsiyonel)
            notlar: Satış notları (opsiyonel)
            
        Returns:
            Oluşturulan satış ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("Sepet ID pozitif olmalıdır")
        
        if terminal_id <= 0:
            raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
        
        if kasiyer_id <= 0:
            raise DogrulamaHatasi("Kasiyer ID pozitif olmalıdır")
        
        if toplam_tutar < 0:
            raise DogrulamaHatasi("Toplam tutar negatif olamaz")
        
        if indirim_tutari and indirim_tutari < 0:
            raise DogrulamaHatasi("İndirim tutarı negatif olamaz")
        
        if musteri_id and musteri_id <= 0:
            raise DogrulamaHatasi("Müşteri ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                # Yeni satış oluştur
                yeni_satis = Satis(
                    sepet_id=sepet_id,
                    terminal_id=terminal_id,
                    kasiyer_id=kasiyer_id,
                    satis_tarihi=datetime.now(),
                    toplam_tutar=toplam_tutar,
                    indirim_tutari=indirim_tutari or Decimal('0.00'),
                    durum=SatisDurum.BEKLEMEDE,
                    musteri_id=musteri_id,
                    notlar=notlar
                )
                
                # Validasyon
                hatalar = satis_validasyon(yeni_satis)
                if hatalar:
                    raise DogrulamaHatasi(f"Satış validasyon hataları: {', '.join(hatalar)}")
                
                session.add(yeni_satis)
                session.commit()
                
                return yeni_satis.id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Satış oluşturma hatası: {str(e)}")
    
    def satis_getir(self, satis_id: int) -> Optional[Dict[str, Any]]:
        """
        Satış bilgilerini getirir
        
        Args:
            satis_id: Satış kimliği
            
        Returns:
            Satış bilgileri dict formatında veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz satış ID
            VeritabaniHatasi: Veritabanı hatası
        """
        if satis_id <= 0:
            raise DogrulamaHatasi("Satış ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                satis = session.query(Satis).options(
                    joinedload(Satis.odemeler)
                ).filter(Satis.id == satis_id).first()
                
                if not satis:
                    return None
                
                # Satış bilgilerini dict'e çevir
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
                    'notlar': satis.notlar,
                    'olusturma_tarihi': satis.olusturma_tarihi.isoformat() if satis.olusturma_tarihi else None,
                    'guncelleme_tarihi': satis.guncelleme_tarihi.isoformat() if satis.guncelleme_tarihi else None,
                    'odemeler': []
                }
                
                # Ödeme bilgilerini ekle
                for odeme in satis.odemeler:
                    odeme_dict = {
                        'id': odeme.id,
                        'odeme_turu': odeme.odeme_turu.value,
                        'tutar': float(odeme.tutar),
                        'referans_no': odeme.referans_no,
                        'odeme_tarihi': odeme.odeme_tarihi.isoformat(),
                        'kart_son_4_hane': odeme.kart_son_4_hane,
                        'banka_kodu': odeme.banka_kodu,
                        'taksit_sayisi': odeme.taksit_sayisi
                    }
                    satis_dict['odemeler'].append(odeme_dict)
                
                # Ek hesaplanan alanlar
                satis_dict['toplam_odeme_tutari'] = float(satis.toplam_odeme_tutari())
                satis_dict['odeme_tamamlandi'] = satis.odeme_tamamlandi_mi()
                satis_dict['kalan_tutar'] = float(satis.kalan_tutar())
                
                return satis_dict
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Satış getirme hatası: {str(e)}")
    
    def satis_durum_guncelle(self, satis_id: int, yeni_durum: SatisDurum, 
                           fis_no: Optional[str] = None) -> bool:
        """
        Satış durumunu günceller
        
        Args:
            satis_id: Satış kimliği
            yeni_durum: Yeni durum
            fis_no: Fiş numarası (tamamlanan satışlar için)
            
        Returns:
            Güncelleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Satış bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if satis_id <= 0:
            raise DogrulamaHatasi("Satış ID pozitif olmalıdır")
        
        if yeni_durum == SatisDurum.TAMAMLANDI and not fis_no:
            raise DogrulamaHatasi("Tamamlanan satış için fiş numarası gereklidir")
        
        with postgresql_session() as session:
            try:
                satis = session.query(Satis).filter(Satis.id == satis_id).first()
                if not satis:
                    raise SontechHatasi(f"Satış bulunamadı: {satis_id}")
                
                satis.durum = yeni_durum
                if fis_no:
                    satis.fis_no = fis_no
                
                # Validasyon
                hatalar = satis_validasyon(satis)
                if hatalar:
                    raise DogrulamaHatasi(f"Satış validasyon hataları: {', '.join(hatalar)}")
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Satış durum güncelleme hatası: {str(e)}")
    
    def satis_iptal_et(self, satis_id: int, iptal_nedeni: str) -> bool:
        """
        Satışı iptal eder
        
        Args:
            satis_id: Satış kimliği
            iptal_nedeni: İptal nedeni
            
        Returns:
            İptal başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Satış bulunamadı veya iptal edilemez
            VeritabaniHatasi: Veritabanı hatası
        """
        if satis_id <= 0:
            raise DogrulamaHatasi("Satış ID pozitif olmalıdır")
        
        if not iptal_nedeni or not iptal_nedeni.strip():
            raise DogrulamaHatasi("İptal nedeni boş olamaz")
        
        with postgresql_session() as session:
            try:
                satis = session.query(Satis).filter(Satis.id == satis_id).first()
                if not satis:
                    raise SontechHatasi(f"Satış bulunamadı: {satis_id}")
                
                # İptal edilebilir durumda mı kontrol et
                if satis.durum == SatisDurum.IPTAL:
                    raise SontechHatasi("Satış zaten iptal edilmiş")
                
                # Durumu iptal olarak güncelle
                satis.durum = SatisDurum.IPTAL
                satis.notlar = f"{satis.notlar or ''}\nİPTAL: {iptal_nedeni}".strip()
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Satış iptal hatası: {str(e)}")
    
    def satis_tamamla(self, satis_id: int, fis_no: str) -> bool:
        """
        Satışı tamamlar
        
        Args:
            satis_id: Satış kimliği
            fis_no: Fiş numarası
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            DogrulamaHatasi: Geçersiz satış kimliği
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with postgresql_session() as session:
                # Satış kaydını getir
                satis = session.query(Satis).filter(Satis.id == satis_id).first()
                
                if not satis:
                    raise DogrulamaHatasi(f"Satış bulunamadı: {satis_id}")
                
                # Satış durumunu tamamlandı olarak işaretle
                satis.durum = SatisDurum.TAMAMLANDI
                satis.fis_no = fis_no
                satis.guncelleme_tarihi = datetime.now()
                
                session.commit()
                return True
                
        except DogrulamaHatasi:
            raise
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Satış tamamlama hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"Satış tamamlama işlemi başarısız: {str(e)}")