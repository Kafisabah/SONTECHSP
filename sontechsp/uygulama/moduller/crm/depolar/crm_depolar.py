# Version: 0.1.0
# Last Update: 2024-12-17
# Module: crm_depolar
# Description: CRM modülü repository katmanı - veritabanı erişim sağlar
# Changelog:
# - İlk oluşturma: MusteriDeposu ve SadakatDeposu sınıfları iskelet
# - MusteriDeposu metodları implement edildi

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import re
from ....cekirdek.hatalar import DogrulamaHatasi, VeritabaniHatasi, AlanHatasi
from ....veritabani.modeller.crm import Musteriler, SadakatPuanlari
from ..dto import MusteriOlusturDTO, MusteriGuncelleDTO, PuanIslemDTO, MusteriAraDTO
from ..sabitler import PuanIslemTuru


class MusteriDeposu:
    """Müşteri veritabanı erişim katmanı"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def musteri_olustur(self, dto: MusteriOlusturDTO) -> Musteriler:
        """Yeni müşteri oluşturur"""
        try:
            # Zorunlu alan kontrolü
            if not dto.ad or not dto.ad.strip():
                raise AlanHatasi("ad", "Ad alanı boş olamaz")
            if not dto.soyad or not dto.soyad.strip():
                raise AlanHatasi("soyad", "Soyad alanı boş olamaz")
            
            # E-posta format kontrolü
            if dto.eposta and not self._eposta_gecerli_mi(dto.eposta):
                raise AlanHatasi("eposta", "Geçersiz e-posta formatı")
            
            # Benzersizlik kontrolleri
            if dto.telefon:
                mevcut_telefon = self.db.query(Musteriler).filter(
                    Musteriler.telefon == dto.telefon
                ).first()
                if mevcut_telefon:
                    raise DogrulamaHatasi("Telefon numarası zaten kayıtlı")
            
            if dto.eposta:
                mevcut_eposta = self.db.query(Musteriler).filter(
                    Musteriler.eposta == dto.eposta
                ).first()
                if mevcut_eposta:
                    raise DogrulamaHatasi("E-posta adresi zaten kayıtlı")
            
            # Yeni müşteri oluştur
            musteri = Musteriler(
                ad=dto.ad.strip(),
                soyad=dto.soyad.strip(),
                telefon=dto.telefon.strip() if dto.telefon else None,
                eposta=dto.eposta.strip().lower() if dto.eposta else None,
                vergi_no=dto.vergi_no.strip() if dto.vergi_no else None,
                adres=dto.adres.strip() if dto.adres else None,
                aktif_mi=dto.aktif_mi
            )
            
            self.db.add(musteri)
            self.db.flush()
            return musteri
            
        except IntegrityError as e:
            raise DogrulamaHatasi(f"Veri bütünlüğü hatası: {str(e)}")
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Müşteri oluşturma hatası: {str(e)}")
    
    def musteri_guncelle(self, musteri_id: int, dto: MusteriGuncelleDTO) -> Musteriler:
        """Mevcut müşteri bilgilerini günceller"""
        try:
            # Müşteriyi getir
            musteri = self.db.get(Musteriler, musteri_id)
            if not musteri:
                raise DogrulamaHatasi(f"ID {musteri_id} ile müşteri bulunamadı")
            
            # Sadece gönderilen alanları güncelle
            if dto.ad is not None:
                if not dto.ad.strip():
                    raise AlanHatasi("ad", "Ad alanı boş olamaz")
                musteri.ad = dto.ad.strip()
            
            if dto.soyad is not None:
                if not dto.soyad.strip():
                    raise AlanHatasi("soyad", "Soyad alanı boş olamaz")
                musteri.soyad = dto.soyad.strip()
            
            if dto.telefon is not None:
                telefon = dto.telefon.strip() if dto.telefon else None
                if telefon:
                    # Benzersizlik kontrolü (kendi kaydı hariç)
                    mevcut_telefon = self.db.query(Musteriler).filter(
                        and_(
                            Musteriler.telefon == telefon,
                            Musteriler.id != musteri_id
                        )
                    ).first()
                    if mevcut_telefon:
                        raise DogrulamaHatasi("Telefon numarası zaten kayıtlı")
                musteri.telefon = telefon
            
            if dto.eposta is not None:
                eposta = dto.eposta.strip().lower() if dto.eposta else None
                if eposta:
                    # E-posta format kontrolü
                    if not self._eposta_gecerli_mi(eposta):
                        raise AlanHatasi("eposta", "Geçersiz e-posta formatı")
                    
                    # Benzersizlik kontrolü (kendi kaydı hariç)
                    mevcut_eposta = self.db.query(Musteriler).filter(
                        and_(
                            Musteriler.eposta == eposta,
                            Musteriler.id != musteri_id
                        )
                    ).first()
                    if mevcut_eposta:
                        raise DogrulamaHatasi("E-posta adresi zaten kayıtlı")
                musteri.eposta = eposta
            
            if dto.vergi_no is not None:
                musteri.vergi_no = dto.vergi_no.strip() if dto.vergi_no else None
            
            if dto.adres is not None:
                musteri.adres = dto.adres.strip() if dto.adres else None
            
            if dto.aktif_mi is not None:
                musteri.aktif_mi = dto.aktif_mi
            
            self.db.flush()
            return musteri
            
        except IntegrityError as e:
            raise DogrulamaHatasi(f"Veri bütünlüğü hatası: {str(e)}")
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Müşteri güncelleme hatası: {str(e)}")
    
    def musteri_getir(self, musteri_id: int) -> Optional[Musteriler]:
        """ID ile müşteri getirir"""
        try:
            return self.db.get(Musteriler, musteri_id)
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Müşteri getirme hatası: {str(e)}")
    
    def musteri_ara(self, dto: MusteriAraDTO) -> List[Musteriler]:
        """Kriterlere göre müşteri arar"""
        try:
            query = self.db.query(Musteriler)
            
            # Filtreler (AND mantığı)
            if dto.ad:
                # Kısmi eşleşme (case-insensitive)
                query = query.filter(
                    Musteriler.ad.ilike(f"%{dto.ad.strip()}%")
                )
            
            if dto.soyad:
                # Kısmi eşleşme (case-insensitive)
                query = query.filter(
                    Musteriler.soyad.ilike(f"%{dto.soyad.strip()}%")
                )
            
            if dto.telefon:
                # Tam eşleşme
                query = query.filter(
                    Musteriler.telefon == dto.telefon.strip()
                )
            
            if dto.eposta:
                # Tam eşleşme (case-insensitive)
                query = query.filter(
                    Musteriler.eposta == dto.eposta.strip().lower()
                )
            
            if dto.aktif_mi is not None:
                query = query.filter(
                    Musteriler.aktif_mi == dto.aktif_mi
                )
            
            # Sonuçları getir
            return query.all()
            
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Müşteri arama hatası: {str(e)}")
    
    def _eposta_gecerli_mi(self, eposta: str) -> bool:
        """E-posta formatının geçerli olup olmadığını kontrol eder"""
        if not eposta:
            return False
        
        # Basit e-posta regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, eposta))


class SadakatDeposu:
    """Sadakat puan veritabanı erişim katmanı"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def puan_kaydi_ekle(self, dto: PuanIslemDTO, islem_turu: PuanIslemTuru) -> SadakatPuanlari:
        """Puan işlem kaydı ekler"""
        try:
            # Müşteri varlık kontrolü
            musteri = self.db.get(Musteriler, dto.musteri_id)
            if not musteri:
                raise DogrulamaHatasi(f"ID {dto.musteri_id} ile müşteri bulunamadı")
            
            # Pozitif puan kontrolü
            if dto.puan <= 0:
                raise AlanHatasi("puan", "Puan değeri pozitif olmalıdır")
            
            # Puan kaydı oluştur
            puan_kaydi = SadakatPuanlari(
                musteri_id=dto.musteri_id,
                islem_turu=islem_turu.value,
                puan=dto.puan,
                aciklama=dto.aciklama.strip() if dto.aciklama else None,
                referans_turu=dto.referans_turu.value if dto.referans_turu else None,
                referans_id=dto.referans_id
            )
            
            self.db.add(puan_kaydi)
            self.db.flush()
            return puan_kaydi
            
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Puan kaydı ekleme hatası: {str(e)}")
    
    def puan_bakiyesi_getir(self, musteri_id: int) -> int:
        """Müşteri puan bakiyesini getirir"""
        try:
            # KAZANIM - HARCAMA formülü ile bakiye hesapla
            kazanim_toplam = self.db.query(
                func.coalesce(func.sum(SadakatPuanlari.puan), 0)
            ).filter(
                and_(
                    SadakatPuanlari.musteri_id == musteri_id,
                    SadakatPuanlari.islem_turu.in_([
                        PuanIslemTuru.KAZANIM.value,
                        PuanIslemTuru.DUZELTME.value
                    ])
                )
            ).scalar()
            
            harcama_toplam = self.db.query(
                func.coalesce(func.sum(SadakatPuanlari.puan), 0)
            ).filter(
                and_(
                    SadakatPuanlari.musteri_id == musteri_id,
                    SadakatPuanlari.islem_turu == PuanIslemTuru.HARCAMA.value
                )
            ).scalar()
            
            # Pozitif düzeltmeleri kazanım olarak say
            pozitif_duzeltme_toplam = self.db.query(
                func.coalesce(func.sum(SadakatPuanlari.puan), 0)
            ).filter(
                and_(
                    SadakatPuanlari.musteri_id == musteri_id,
                    SadakatPuanlari.islem_turu == PuanIslemTuru.DUZELTME.value,
                    SadakatPuanlari.puan > 0
                )
            ).scalar()
            
            # Negatif düzeltmeleri harcama olarak say
            negatif_duzeltme_toplam = self.db.query(
                func.coalesce(func.sum(func.abs(SadakatPuanlari.puan)), 0)
            ).filter(
                and_(
                    SadakatPuanlari.musteri_id == musteri_id,
                    SadakatPuanlari.islem_turu == PuanIslemTuru.DUZELTME.value,
                    SadakatPuanlari.puan < 0
                )
            ).scalar()
            
            bakiye = (kazanim_toplam + pozitif_duzeltme_toplam) - (harcama_toplam + negatif_duzeltme_toplam)
            return max(0, bakiye)  # Negatif bakiye olmaz
            
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Puan bakiyesi getirme hatası: {str(e)}")
    
    def puan_hareketleri_listele(self, musteri_id: int, limit: int = 100) -> List[SadakatPuanlari]:
        """Müşteri puan hareketlerini listeler"""
        try:
            query = self.db.query(SadakatPuanlari).filter(
                SadakatPuanlari.musteri_id == musteri_id
            ).order_by(
                SadakatPuanlari.olusturma_tarihi.desc()
            ).limit(limit)
            
            return query.all()
            
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Puan hareketleri listeleme hatası: {str(e)}")