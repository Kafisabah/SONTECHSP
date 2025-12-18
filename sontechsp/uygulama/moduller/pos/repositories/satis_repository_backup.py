# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.repositories.satis_repository
# Description: Satış repository implementasyonu
# Changelog:
# - İlk oluşturma

"""
Satış Repository Implementasyonu

Bu modül satış ve ödeme veri erişim işlemlerini yönetir.
Transaction desteği ile satış kayıtları yönetimi sağlar.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc

from sontechsp.uygulama.veritabani.baglanti import postgresql_session
from sontechsp.uygulama.moduller.pos.arayuzler import ISatisRepository, SatisDurum, OdemeTuru
from sontechsp.uygulama.moduller.pos.database.models.satis import (
    Satis, SatisOdeme, satis_validasyon, satis_odeme_validasyon
)
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, DogrulamaHatasi, SontechHatasi
)


class SatisRepository(ISatisRepository):
    """
    Satış repository implementasyonu
    
    Satış ve ödeme CRUD operasyonlarını yönetir.
    PostgreSQL veritabanı ile transaction desteği sağlar.
    """
    
    def __init__(self):
        """Repository'yi başlatır"""
        pass
    
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
    
    def gunluk_satis_ozeti(self, terminal_id: int, tarih: datetime) -> Dict[str, Any]:
        """
        Günlük satış özetini getirir
        
        Args:
            terminal_id: Terminal kimliği
            tarih: Özet tarihi
            
        Returns:
            Günlük satış özeti
            
        Raises:
            DogrulamaHatasi: Geçersiz parametreler
            VeritabaniHatasi: Veritabanı hatası
        """
        if terminal_id <= 0:
            raise DogrulamaHatasi("Terminal ID pozitif olmalıdır")
        
        with postgresql_session() as session:
            try:
                # Günün başı ve sonu
                gun_baslangic = tarih.replace(hour=0, minute=0, second=0, microsecond=0)
                gun_bitis = tarih.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                # Tamamlanan satışları getir
                satislar = session.query(Satis).filter(
                    and_(
                        Satis.terminal_id == terminal_id,
                        Satis.satis_tarihi >= gun_baslangic,
                        Satis.satis_tarihi <= gun_bitis,
                        Satis.durum == SatisDurum.TAMAMLANDI
                    )
                ).all()
                
                # Özet hesapla
                toplam_satis_sayisi = len(satislar)
                toplam_tutar = sum(satis.net_tutar_hesapla() for satis in satislar)
                toplam_indirim = sum(satis.indirim_tutari for satis in satislar)
                
                # Ödeme türü bazında özet
                odeme_ozeti = {}
                for satis in satislar:
                    for odeme in satis.odemeler:
                        turu = odeme.odeme_turu.value
                        if turu not in odeme_ozeti:
                            odeme_ozeti[turu] = {'adet': 0, 'tutar': 0.0}
                        odeme_ozeti[turu]['adet'] += 1
                        odeme_ozeti[turu]['tutar'] += float(odeme.tutar)
                
                return {
                    'tarih': tarih.date().isoformat(),
                    'terminal_id': terminal_id,
                    'toplam_satis_sayisi': toplam_satis_sayisi,
                    'toplam_tutar': float(toplam_tutar),
                    'toplam_indirim': float(toplam_indirim),
                    'net_tutar': float(toplam_tutar),
                    'odeme_ozeti': odeme_ozeti
                }
                
            except SQLAlchemyError as e:
                raise VeritabaniHatasi(f"Günlük özet hatası: {str(e)}")
    
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