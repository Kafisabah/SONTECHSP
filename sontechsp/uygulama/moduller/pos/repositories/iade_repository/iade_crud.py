# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.iade_repository.iade_crud
# Description: İade CRUD işlemleri
# Changelog:
# - Refactoring: Ana dosyadan CRUD işlemleri ayrıldı

"""
İade CRUD İşlemleri

Bu modül iade ve iade satırı temel CRUD operasyonlarını yönetir.
Oluşturma, okuma, güncelleme ve silme işlemleri sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.arayuzler import IIadeRepository, SatisDurum
from sontechsp.uygulama.moduller.pos.database.models.iade import (
    Iade, IadeSatiri, iade_validasyon, iade_satiri_validasyon
)
from sontechsp.uygulama.moduller.pos.database.models.satis import Satis
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class IadeCrud:
    """
    İade CRUD işlemleri sınıfı
    
    Temel iade ve iade satırı CRUD operasyonlarını yönetir.
    """
    
    def iade_olustur(self, orijinal_satis_id: int, terminal_id: int, kasiyer_id: int,
                    neden: str, musteri_id: Optional[int] = None, 
                    notlar: Optional[str] = None) -> int:
        """
        Yeni iade kaydı oluşturur
        
        Args:
            orijinal_satis_id: Orijinal satış kimliği
            terminal_id: Terminal kimliği
            kasiyer_id: Kasiyer kimliği
            neden: İade nedeni
            musteri_id: Müşteri kimliği (opsiyonel)
            notlar: İade notları (opsiyonel)
            
        Returns:
            Oluşturulan iade ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: Orijinal satış bulunamadı veya iade edilemez
            VeritabaniHatasi: Veritabanı hatası
        """
        if orijinal_satis_id <= 0:
            raise DogrulamaHatasi("Orijinal satış ID pozitif olmalıdır")
        
        if terminal_id <= 0:
            raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
        
        if kasiyer_id <= 0:
            raise DogrulamaHatasi("Kasiyer ID pozitif olmalıdır")
        
        if not neden or not neden.strip():
            raise DogrulamaHatasi("İade nedeni boş olamaz")
        
        if musteri_id and musteri_id <= 0:
            raise DogrulamaHatasi("Müşteri ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                # Orijinal satış var mı ve iade edilebilir mi kontrol et
                orijinal_satis = session.query(Satis).filter(Satis.id == orijinal_satis_id).first()
                if not orijinal_satis:
                    raise SontechHatasi(f"Orijinal satış bulunamadı: {orijinal_satis_id}")
                
                if orijinal_satis.durum != SatisDurum.TAMAMLANDI:
                    raise SontechHatasi("Sadece tamamlanan satışlar iade edilebilir")
                
                # Yeni iade oluştur
                yeni_iade = Iade(
                    orijinal_satis_id=orijinal_satis_id,
                    terminal_id=terminal_id,
                    kasiyer_id=kasiyer_id,
                    iade_tarihi=datetime.now(),
                    toplam_tutar=Decimal('0.00'),  # Satırlar eklendikçe güncellenecek
                    neden=neden.strip(),
                    musteri_id=musteri_id,
                    notlar=notlar
                )
                
                # Validasyon (parametreler üzerinde)
                hatalar = []
                if orijinal_satis_id <= 0:
                    hatalar.append("Orijinal satış ID pozitif olmalıdır")
                if terminal_id <= 0:
                    hatalar.append("Terminal ID pozitif olmalıdır")
                if kasiyer_id <= 0:
                    hatalar.append("Kasiyer ID pozitif olmalıdır")
                if not neden or not neden.strip():
                    hatalar.append("İade nedeni boş olamaz")
                
                if hatalar:
                    raise DogrulamaHatasi(f"İade validasyon hataları: {', '.join(hatalar)}")
                
                session.add(yeni_iade)
                session.commit()
                
                return yeni_iade.id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"İade oluşturma hatası: {str(e)}")
    
    def iade_getir(self, iade_id: int) -> Optional[Dict[str, Any]]:
        """
        İade bilgilerini getirir
        
        Args:
            iade_id: İade kimliği
            
        Returns:
            İade bilgileri dict formatında veya None
            
        Raises:
            DogrulamaHatasi: Geçersiz iade ID
            VeritabaniHatasi: Veritabanı hatası
        """
        if iade_id <= 0:
            raise DogrulamaHatasi("İade ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                iade = session.query(Iade).options(
                    joinedload(Iade.satirlar)
                ).filter(Iade.id == iade_id).first()
                
                if not iade:
                    return None
                
                # İade bilgilerini dict'e çevir
                iade_dict = {
                    'id': iade.id,
                    'orijinal_satis_id': iade.orijinal_satis_id,
                    'terminal_id': iade.terminal_id,
                    'kasiyer_id': iade.kasiyer_id,
                    'iade_tarihi': iade.iade_tarihi.isoformat(),
                    'toplam_tutar': float(iade.toplam_tutar),
                    'neden': iade.neden,
                    'musteri_id': iade.musteri_id,
                    'notlar': iade.notlar,
                    'fis_no': iade.fis_no,
                    'olusturma_tarihi': iade.olusturma_tarihi.isoformat() if iade.olusturma_tarihi else None,
                    'guncelleme_tarihi': iade.guncelleme_tarihi.isoformat() if iade.guncelleme_tarihi else None,
                    'satirlar': []
                }
                
                # İade satırlarını ekle
                for satir in iade.satirlar:
                    satir_dict = {
                        'id': satir.id,
                        'urun_id': satir.urun_id,
                        'barkod': satir.barkod,
                        'urun_adi': satir.urun_adi,
                        'adet': satir.adet,
                        'birim_fiyat': float(satir.birim_fiyat),
                        'toplam_tutar': float(satir.toplam_tutar),
                        'orijinal_sepet_satiri_id': satir.orijinal_sepet_satiri_id,
                        'iade_nedeni': satir.iade_nedeni
                    }
                    iade_dict['satirlar'].append(satir_dict)
                
                # Ek hesaplanan alanlar
                iade_dict['satir_sayisi'] = iade.satir_sayisi()
                iade_dict['toplam_adet'] = iade.toplam_adet()
                iade_dict['hesaplanan_toplam_tutar'] = float(iade.hesaplanan_toplam_tutar())
                
                return iade_dict
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"İade getirme hatası: {str(e)}")
    
    def iade_satiri_ekle(self, iade_id: int, urun_id: int, barkod: str, urun_adi: str,
                        adet: int, birim_fiyat: Decimal, 
                        orijinal_sepet_satiri_id: Optional[int] = None,
                        iade_nedeni: Optional[str] = None) -> int:
        """
        İadeye satır ekler
        
        Args:
            iade_id: İade kimliği
            urun_id: Ürün kimliği
            barkod: Ürün barkodu
            urun_adi: Ürün adı
            adet: İade edilen adet
            birim_fiyat: Birim fiyat
            orijinal_sepet_satiri_id: Orijinal sepet satırı kimliği (opsiyonel)
            iade_nedeni: Bu satır için özel iade nedeni (opsiyonel)
            
        Returns:
            Oluşturulan satır ID'si
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: İade bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if iade_id <= 0:
            raise DogrulamaHatasi("İade ID pozitif olmalıdır")
        
        if urun_id <= 0:
            raise DogrulamaHatasi("Ürün ID pozitif olmalıdır")
        
        if not barkod or not barkod.strip():
            raise DogrulamaHatasi("Barkod boş olamaz")
        
        if not urun_adi or not urun_adi.strip():
            raise DogrulamaHatasi("Ürün adı boş olamaz")
        
        if adet <= 0:
            raise DogrulamaHatasi("Adet pozitif olmalıdır")
        
        if birim_fiyat < 0:
            raise DogrulamaHatasi("Birim fiyat negatif olamaz")
        
        with postgresql_session() as session:
            try:
                # İade var mı kontrol et
                iade = session.query(Iade).filter(Iade.id == iade_id).first()
                if not iade:
                    raise SontechHatasi(f"İade bulunamadı: {iade_id}")
                
                # Yeni satır oluştur
                yeni_satir = IadeSatiri(
                    iade_id=iade_id,
                    urun_id=urun_id,
                    barkod=barkod.strip(),
                    urun_adi=urun_adi.strip(),
                    adet=adet,
                    birim_fiyat=birim_fiyat,
                    toplam_tutar=Decimal(str(adet)) * birim_fiyat,
                    orijinal_sepet_satiri_id=orijinal_sepet_satiri_id,
                    iade_nedeni=iade_nedeni
                )
                
                # Validasyon
                hatalar = iade_satiri_validasyon(yeni_satir)
                if hatalar:
                    raise DogrulamaHatasi(f"İade satırı validasyon hataları: {', '.join(hatalar)}")
                
                session.add(yeni_satir)
                session.flush()
                
                # İade toplamını güncelle
                self._iade_toplam_guncelle(session, iade_id)
                
                session.commit()
                return yeni_satir.id
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"İade satırı ekleme hatası: {str(e)}")
    
    def iade_satiri_guncelle(self, satir_id: int, adet: int) -> bool:
        """
        İade satırını günceller
        
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
            raise DogrulamaHatasi("Satır ID pozitif olmalıdır")
        
        if adet <= 0:
            raise DogrulamaHatasi("Adet pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                satir = session.query(IadeSatiri).filter(IadeSatiri.id == satir_id).first()
                if not satir:
                    raise SontechHatasi(f"İade satırı bulunamadı: {satir_id}")
                
                # Adedi güncelle
                satir.adet = adet
                satir.toplam_tutar_guncelle()
                
                # Validasyon
                hatalar = iade_satiri_validasyon(satir)
                if hatalar:
                    raise DogrulamaHatasi(f"İade satırı validasyon hataları: {', '.join(hatalar)}")
                
                # İade toplamını güncelle
                self._iade_toplam_guncelle(session, satir.iade_id)
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"İade satırı güncelleme hatası: {str(e)}")
    
    def iade_satiri_sil(self, satir_id: int) -> bool:
        """
        İade satırını siler
        
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
            raise DogrulamaHatasi("Satır ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                satir = session.query(IadeSatiri).filter(IadeSatiri.id == satir_id).first()
                if not satir:
                    raise SontechHatasi(f"İade satırı bulunamadı: {satir_id}")
                
                iade_id = satir.iade_id
                
                # Satırı sil
                session.delete(satir)
                
                # İade toplamını güncelle
                self._iade_toplam_guncelle(session, iade_id)
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"İade satırı silme hatası: {str(e)}")
    
    def iade_fis_no_guncelle(self, iade_id: int, fis_no: str) -> bool:
        """
        İade fiş numarasını günceller
        
        Args:
            iade_id: İade kimliği
            fis_no: Fiş numarası
            
        Returns:
            Güncelleme başarılı mı
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            SontechHatasi: İade bulunamadı
            VeritabaniHatasi: Veritabanı hatası
        """
        if iade_id <= 0:
            raise DogrulamaHatasi("İade ID pozitif olmalıdır")
        
        if not fis_no or not fis_no.strip():
            raise DogrulamaHatasi("Fiş numarası boş olamaz")
        
        with postgresql_session() as session:
            try:
                iade = session.query(Iade).filter(Iade.id == iade_id).first()
                if not iade:
                    raise SontechHatasi(f"İade bulunamadı: {iade_id}")
                
                iade.fis_no = fis_no.strip()
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                raise VeritabaniHatasi(f"İade fiş numarası güncelleme hatası: {str(e)}")
    
    def iade_tamamla(self, iade_id: int) -> bool:
        """
        İadeyi tamamlar
        
        Args:
            iade_id: İade kimliği
            
        Returns:
            İşlem başarılı ise True
            
        Raises:
            DogrulamaHatasi: Geçersiz iade kimliği
            VeritabaniHatasi: Veritabanı hatası
        """
        try:
            with postgresql_session() as session:
                # İade kaydını getir
                iade = session.query(Iade).filter(Iade.id == iade_id).first()
                
                if not iade:
                    raise DogrulamaHatasi(f"İade bulunamadı: {iade_id}")
                
                # İade durumunu tamamlandı olarak işaretle
                iade.durum = "TAMAMLANDI"
                iade.guncelleme_tarihi = datetime.now()
                
                session.commit()
                return True
                
        except DogrulamaHatasi:
            raise
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"İade tamamlama hatası: {str(e)}")
        except Exception as e:
            raise SontechHatasi(f"İade tamamlama işlemi başarısız: {str(e)}")
    
    def _iade_toplam_guncelle(self, session: Session, iade_id: int) -> None:
        """
        İade toplamını günceller (private method)
        
        Args:
            session: Veritabanı session'ı
            iade_id: İade kimliği
        """
        iade = session.query(Iade).filter(Iade.id == iade_id).first()
        if iade:
            # Tüm satırların toplamını hesapla
            satirlar = session.query(IadeSatiri).filter(IadeSatiri.iade_id == iade_id).all()
            toplam = sum(satir.toplam_tutar for satir in satirlar)
            iade.toplam_tutar = toplam
            session.flush()