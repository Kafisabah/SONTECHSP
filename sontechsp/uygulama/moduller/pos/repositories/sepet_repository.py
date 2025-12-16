# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.repositories.sepet_repository
# Description: Sepet repository implementasyonu
# Changelog:
# - İlk oluşturma

"""
Sepet Repository Implementasyonu

Bu modül sepet ve sepet satırı veri erişim işlemlerini yönetir.
CRUD operasyonları ve sepet satırı yönetimi sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.arayuzler import ISepetRepository, SepetDurum
from sontechsp.uygulama.moduller.pos.database.models.sepet import (
    Sepet, SepetSatiri, sepet_validasyon, sepet_satiri_validasyon
)
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class SepetRepository(ISepetRepository):
    """
    Sepet repository implementasyonu
    
    Sepet ve sepet satırı CRUD operasyonlarını yönetir.
    PostgreSQL veritabanı ile çalışır.
    """
    
    def __init__(self):
        """Repository'yi başlatır"""
        pass
    
    def sepet_olustur(self, terminal_id: int, kasiyer_id: int) -> int:
        """
        Yeni sepet oluşturur
        
        Args:
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            
        Returns:
            Oluşturulan sepet ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if terminal_id <= 0:
            raise DogrulamaHatasi("terminal_id_pozitif", "Terminal ID pozitif olmalıdır")
        
        if kasiyer_id <= 0:
            raise DogrulamaHatasi("kasiyer_id_pozitif", "Kasiyer ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                # Mevcut aktif sepet var mı kontrol et
                mevcut_sepet = session.query(Sepet).filter(
                    and_(
                        Sepet.terminal_id == terminal_id,
                        Sepet.durum == SepetDurum.AKTIF
                    )
                ).first()
                
                if mevcut_sepet:
                    # Mevcut sepeti beklemede durumuna getir
                    mevcut_sepet.durum = SepetDurum.BEKLEMEDE
                    session.flush()
                
                # Yeni sepet oluştur
                yeni_sepet = Sepet(
                    terminal_id=terminal_id,
                    kasiyer_id=kasiyer_id,
                    durum=SepetDurum.AKTIF,
                    toplam_tutar=Decimal('0.00'),
                    indirim_tutari=Decimal('0.00')
                )
                
                # Validasyon
                hatalar = sepet_validasyon(yeni_sepet)
                if hatalar:
                    raise DogrulamaHatasi("sepet_validasyon", f"Sepet validasyon hataları: {', '.join(hatalar)}")
                
                session.add(yeni_sepet)
                session.commit()
                
                return yeni_sepet.id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Sepet oluşturma hatası: {str(e)}")
    
    def sepet_getir(self, sepet_id: int) -> Optional[Dict[str, Any]]:
        """
        Sepet bilgilerini getirir
        
        Args:
            sepet_id: Sepet kimliği
            
        Returns:
            Sepet bilgileri dict formatında veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz sepet ID
            VeritabaniHatasi: Veritabanı hatası
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id_pozitif", "Sepet ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                sepet = session.query(Sepet).options(
                    joinedload(Sepet.satirlar)
                ).filter(Sepet.id == sepet_id).first()
                
                if not sepet:
                    return None
                
                # Sepet bilgilerini dict'e çevir
                sepet_dict = {
                    'id': sepet.id,
                    'terminal_id': sepet.terminal_id,
                    'kasiyer_id': sepet.kasiyer_id,
                    'durum': sepet.durum.value,
                    'toplam_tutar': float(sepet.toplam_tutar),
                    'indirim_tutari': float(sepet.indirim_tutari),
                    'net_tutar': float(sepet.net_tutar_hesapla()),
                    'olusturma_tarihi': sepet.olusturma_tarihi.isoformat() if sepet.olusturma_tarihi else None,
                    'guncelleme_tarihi': sepet.guncelleme_tarihi.isoformat() if sepet.guncelleme_tarihi else None,
                    'satirlar': []
                }
                
                # Sepet satırlarını ekle
                for satir in sepet.satirlar:
                    satir_dict = {
                        'id': satir.id,
                        'urun_id': satir.urun_id,
                        'barkod': satir.barkod,
                        'urun_adi': satir.urun_adi,
                        'adet': satir.adet,
                        'birim_fiyat': float(satir.birim_fiyat),
                        'indirim_tutari': float(satir.indirim_tutari),
                        'toplam_tutar': float(satir.toplam_tutar)
                    }
                    sepet_dict['satirlar'].append(satir_dict)
                
                return sepet_dict
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Sepet getirme hatası: {str(e)}")
    
    def sepet_satiri_ekle(self, sepet_id: int, urun_id: int, barkod: str, 
                         adet: int, birim_fiyat: Decimal) -> int:
        """
        Sepete satır ekler
        
        Args:
            sepet_id: Sepet kimliği
            urun_id: Ürün kimliği
            barkod: Ürün barkodu
            adet: Ürün adedi
            birim_fiyat: Birim fiyat
            
        Returns:
            Oluşturulan satır ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Sepet bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id", "Sepet ID pozitif olmalıdır")
        
        if urun_id <= 0:
            raise DogrulamaHatasi("urun_id", "Ürün ID pozitif olmalıdır")
        
        if not barkod or not barkod.strip():
            raise DogrulamaHatasi("barkod", "Barkod boş olamaz")
        
        if adet <= 0:
            raise DogrulamaHatasi("adet", "Adet pozitif olmalıdır")
        
        if birim_fiyat <= 0:
            raise DogrulamaHatasi("birim_fiyat", "Birim fiyat pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                # Sepet var mı kontrol et
                sepet = session.query(Sepet).filter(Sepet.id == sepet_id).first()
                if not sepet:
                    raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")
                
                # Aynı ürün zaten sepette var mı kontrol et
                mevcut_satir = session.query(SepetSatiri).filter(
                    and_(
                        SepetSatiri.sepet_id == sepet_id,
                        SepetSatiri.urun_id == urun_id
                    )
                ).first()
                
                if mevcut_satir:
                    # Mevcut satırın adedini artır
                    mevcut_satir.adet += adet
                    mevcut_satir.toplam_tutar_guncelle()
                    
                    # Validasyon
                    hatalar = sepet_satiri_validasyon(mevcut_satir)
                    if hatalar:
                        raise DogrulamaHatasi("satir_validasyon", f"Satır validasyon hataları: {', '.join(hatalar)}")
                    
                    session.flush()
                    satir_id = mevcut_satir.id
                else:
                    # Yeni satır oluştur
                    yeni_satir = SepetSatiri(
                        sepet_id=sepet_id,
                        urun_id=urun_id,
                        barkod=barkod.strip(),
                        urun_adi=f"Ürün {urun_id}",  # Gerçek implementasyonda stok servisinden alınacak
                        adet=adet,
                        birim_fiyat=birim_fiyat,
                        indirim_tutari=Decimal('0.00'),
                        toplam_tutar=Decimal(str(adet)) * birim_fiyat
                    )
                    
                    # Validasyon
                    hatalar = sepet_satiri_validasyon(yeni_satir)
                    if hatalar:
                        raise DogrulamaHatasi("satir_validasyon", f"Satır validasyon hataları: {', '.join(hatalar)}")
                    
                    session.add(yeni_satir)
                    session.flush()
                    satir_id = yeni_satir.id
                
                # Sepet toplamını güncelle
                self._sepet_toplam_guncelle(session, sepet_id)
                
                session.commit()
                return satir_id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Sepet satırı ekleme hatası: {str(e)}")
    
    def sepet_satiri_guncelle(self, satir_id: int, adet: int) -> bool:
        """
        Sepet satırını günceller
        
        Args:
            satir_id: Satır kimliği
            adet: Yeni adet
            
        Returns:
            Güncelleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Satır bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if satir_id <= 0:
            raise DogrulamaHatasi("satir_id", "Satır ID pozitif olmalıdır")
        
        if adet <= 0:
            raise DogrulamaHatasi("adet", "Adet pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                satir = session.query(SepetSatiri).filter(SepetSatiri.id == satir_id).first()
                if not satir:
                    raise SontechHatasi(f"Sepet satırı bulunamadı: {satir_id}")
                
                # Adedi güncelle
                satir.adet = adet
                satir.toplam_tutar_guncelle()
                
                # Validasyon
                hatalar = sepet_satiri_validasyon(satir)
                if hatalar:
                    raise DogrulamaHatasi("satir_validasyon", f"Satır validasyon hataları: {', '.join(hatalar)}")
                
                # Sepet toplamını güncelle
                self._sepet_toplam_guncelle(session, satir.sepet_id)
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Sepet satırı güncelleme hatası: {str(e)}")
    
    def sepet_satiri_sil(self, satir_id: int) -> bool:
        """
        Sepet satırını siler
        
        Args:
            satir_id: Satır kimliği
            
        Returns:
            Silme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz satır ID
            SontechHatasi: Satır bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if satir_id <= 0:
            raise DogrulamaHatasi("satir_id", "Satır ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                satir = session.query(SepetSatiri).filter(SepetSatiri.id == satir_id).first()
                if not satir:
                    raise SontechHatasi(f"Sepet satırı bulunamadı: {satir_id}")
                
                sepet_id = satir.sepet_id
                
                # Satırı sil
                session.delete(satir)
                
                # Sepet toplamını güncelle
                self._sepet_toplam_guncelle(session, sepet_id)
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Sepet satırı silme hatası: {str(e)}")
    
    def sepet_bosalt(self, sepet_id: int) -> bool:
        """
        Sepeti boşaltır
        
        Args:
            sepet_id: Sepet kimliği
            
        Returns:
            Boşaltma başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz sepet ID
            SontechHatasi: Sepet bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id", "Sepet ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                sepet = session.query(Sepet).filter(Sepet.id == sepet_id).first()
                if not sepet:
                    raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")
                
                # Tüm satırları sil
                session.query(SepetSatiri).filter(SepetSatiri.sepet_id == sepet_id).delete()
                
                # Sepet toplamını sıfırla
                sepet.toplam_tutar = Decimal('0.00')
                sepet.indirim_tutari = Decimal('0.00')
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Sepet boşaltma hatası: {str(e)}")
    
    def terminal_aktif_sepet_getir(self, terminal_id: int) -> Optional[Dict[str, Any]]:
        """
        Terminal için aktif sepeti getirir
        
        Args:
            terminal_id: Terminal kimliği
            
        Returns:
            Aktif sepet bilgileri veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz terminal ID
            VeritabaniHatasi: Veritabanı hatası
        """
        if terminal_id <= 0:
            raise DogrulamaHatasi("terminal_id", "Terminal ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                sepet = session.query(Sepet).filter(
                    and_(
                        Sepet.terminal_id == terminal_id,
                        Sepet.durum == SepetDurum.AKTIF
                    )
                ).first()
                
                if not sepet:
                    return None
                
                return self.sepet_getir(sepet.id)
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Aktif sepet getirme hatası: {str(e)}")
    
    def sepet_durum_guncelle(self, sepet_id: int, yeni_durum: SepetDurum) -> bool:
        """
        Sepet durumunu günceller
        
        Args:
            sepet_id: Sepet kimliği
            yeni_durum: Yeni durum
            
        Returns:
            Güncelleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Sepet bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if sepet_id <= 0:
            raise DogrulamaHatasi("sepet_id", "Sepet ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                sepet = session.query(Sepet).filter(Sepet.id == sepet_id).first()
                if not sepet:
                    raise SontechHatasi(f"Sepet bulunamadı: {sepet_id}")
                
                sepet.durum = yeni_durum
                
                # Validasyon
                hatalar = sepet_validasyon(sepet)
                if hatalar:
                    raise DogrulamaHatasi("sepet_validasyon", f"Sepet validasyon hataları: {', '.join(hatalar)}")
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"Sepet durum güncelleme hatası: {str(e)}")
    
    def _sepet_toplam_guncelle(self, session: Session, sepet_id: int) -> None:
        """
        Sepet toplamını günceller (private method)
        
        Args:
            session: Veritabanı session'ı
            sepet_id: Sepet kimliği
        """
        sepet = session.query(Sepet).filter(Sepet.id == sepet_id).first()
        if sepet:
            # Tüm satırların toplamını hesapla
            satirlar = session.query(SepetSatiri).filter(SepetSatiri.sepet_id == sepet_id).all()
            toplam = sum(satir.toplam_tutar for satir in satirlar)
            sepet.toplam_tutar = toplam
            session.flush()