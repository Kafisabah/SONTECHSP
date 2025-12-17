# Version: 0.1.0
# Last Update: 2024-12-17
# Module: crm_servisler
# Description: CRM modülü servis katmanı - iş mantığı sağlar
# Changelog:
# - İlk oluşturma: MusteriServisi ve SadakatServisi sınıfları iskelet
# - MusteriServisi metodları implement edildi

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .depolar import MusteriDeposu, SadakatDeposu
from .dto import MusteriOlusturDTO, MusteriGuncelleDTO, PuanIslemDTO, MusteriAraDTO
from .sabitler import PuanIslemTuru
from ...veritabani.modeller.crm import Musteriler, SadakatPuanlari
from ...cekirdek.hatalar import DogrulamaHatasi, VeritabaniHatasi


class MusteriServisi:
    """Müşteri iş mantığı servisi"""
    
    def __init__(self, db: Session):
        self.db = db
        self.depo = MusteriDeposu(db)
    
    def musteri_olustur(self, dto: MusteriOlusturDTO) -> Musteriler:
        """Yeni müşteri oluşturur - validation ve hata yönetimi ile"""
        try:
            # İş kuralı validasyonları
            if not dto.ad or not dto.ad.strip():
                raise DogrulamaHatasi("Ad alanı zorunludur")
            if not dto.soyad or not dto.soyad.strip():
                raise DogrulamaHatasi("Soyad alanı zorunludur")
            
            # Repository katmanına delege et
            musteri = self.depo.musteri_olustur(dto)
            self.db.commit()
            return musteri
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise VeritabaniHatasi(f"Müşteri oluşturma işlemi başarısız: {str(e)}")
    
    def musteri_guncelle(self, musteri_id: int, dto: MusteriGuncelleDTO) -> Musteriler:
        """Müşteri bilgilerini günceller - validation ile"""
        try:
            # ID validasyonu
            if not isinstance(musteri_id, int) or musteri_id <= 0:
                raise DogrulamaHatasi("Geçersiz müşteri ID'si")
            
            # Repository katmanına delege et
            musteri = self.depo.musteri_guncelle(musteri_id, dto)
            self.db.commit()
            return musteri
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise VeritabaniHatasi(f"Müşteri güncelleme işlemi başarısız: {str(e)}")
    
    def musteri_getir(self, musteri_id: int) -> Optional[Musteriler]:
        """ID ile müşteri getirir"""
        try:
            # ID validasyonu
            if not isinstance(musteri_id, int) or musteri_id <= 0:
                raise DogrulamaHatasi("Geçersiz müşteri ID'si")
            
            return self.depo.musteri_getir(musteri_id)
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            raise
        except Exception as e:
            raise VeritabaniHatasi(f"Müşteri getirme işlemi başarısız: {str(e)}")
    
    def musteri_ara(self, dto: MusteriAraDTO) -> List[Musteriler]:
        """Kriterlere göre müşteri arar"""
        try:
            # En az bir arama kriteri olmalı
            if not any([dto.ad, dto.soyad, dto.telefon, dto.eposta, dto.aktif_mi is not None]):
                return []  # Boş liste döndür
            
            return self.depo.musteri_ara(dto)
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            raise
        except Exception as e:
            raise VeritabaniHatasi(f"Müşteri arama işlemi başarısız: {str(e)}")


class SadakatServisi:
    """Sadakat programı iş mantığı servisi"""
    
    def __init__(self, db: Session):
        self.db = db
        self.depo = SadakatDeposu(db)
    
    def puan_kazan(self, dto: PuanIslemDTO) -> SadakatPuanlari:
        """Müşteri puan kazanımı işlemi"""
        try:
            # İş kuralı validasyonları
            if dto.puan <= 0:
                raise DogrulamaHatasi("Puan değeri pozitif olmalıdır")
            
            # Repository katmanına delege et
            puan_kaydi = self.depo.puan_kaydi_ekle(dto, PuanIslemTuru.KAZANIM)
            self.db.commit()
            return puan_kaydi
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise VeritabaniHatasi(f"Puan kazanım işlemi başarısız: {str(e)}")
    
    def puan_harca(self, dto: PuanIslemDTO) -> SadakatPuanlari:
        """Müşteri puan harcama işlemi - bakiye kontrolü ile"""
        try:
            # İş kuralı validasyonları
            if dto.puan <= 0:
                raise DogrulamaHatasi("Puan değeri pozitif olmalıdır")
            
            # Bakiye kontrolü
            mevcut_bakiye = self.depo.puan_bakiyesi_getir(dto.musteri_id)
            if mevcut_bakiye < dto.puan:
                raise DogrulamaHatasi(f"Yetersiz bakiye. Mevcut: {mevcut_bakiye}, İstenen: {dto.puan}")
            
            # Repository katmanına delege et
            puan_kaydi = self.depo.puan_kaydi_ekle(dto, PuanIslemTuru.HARCAMA)
            self.db.commit()
            return puan_kaydi
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise VeritabaniHatasi(f"Puan harcama işlemi başarısız: {str(e)}")
    
    def bakiye_getir(self, musteri_id: int) -> int:
        """Müşteri puan bakiyesini getirir"""
        try:
            # ID validasyonu
            if not isinstance(musteri_id, int) or musteri_id <= 0:
                raise DogrulamaHatasi("Geçersiz müşteri ID'si")
            
            return self.depo.puan_bakiyesi_getir(musteri_id)
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            raise
        except Exception as e:
            raise VeritabaniHatasi(f"Bakiye getirme işlemi başarısız: {str(e)}")
    
    def hareketler(self, musteri_id: int, limit: int = 100) -> List[SadakatPuanlari]:
        """Müşteri puan hareketlerini listeler"""
        try:
            # ID validasyonu
            if not isinstance(musteri_id, int) or musteri_id <= 0:
                raise DogrulamaHatasi("Geçersiz müşteri ID'si")
            
            # Limit validasyonu
            if limit <= 0:
                limit = 100  # Varsayılan değer
            
            return self.depo.puan_hareketleri_listele(musteri_id, limit)
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            raise
        except Exception as e:
            raise VeritabaniHatasi(f"Hareket listeleme işlemi başarısız: {str(e)}")
    
    def puan_duzelt(self, dto: PuanIslemDTO) -> SadakatPuanlari:
        """Puan düzeltme işlemi - pozitif/negatif kontrolleri ile"""
        try:
            # İş kuralı validasyonları
            if dto.puan == 0:
                raise DogrulamaHatasi("Düzeltme puanı sıfır olamaz")
            
            # Açıklama zorunluluğu
            if not dto.aciklama or not dto.aciklama.strip():
                raise DogrulamaHatasi("Puan düzeltme işlemi için açıklama zorunludur")
            
            # Negatif düzeltme için bakiye kontrolü
            if dto.puan < 0:
                mevcut_bakiye = self.depo.puan_bakiyesi_getir(dto.musteri_id)
                if mevcut_bakiye < abs(dto.puan):
                    raise DogrulamaHatasi(f"Yetersiz bakiye. Mevcut: {mevcut_bakiye}, Düzeltme: {abs(dto.puan)}")
            
            # Repository katmanına delege et
            puan_kaydi = self.depo.puan_kaydi_ekle(dto, PuanIslemTuru.DUZELTME)
            self.db.commit()
            return puan_kaydi
            
        except (DogrulamaHatasi, VeritabaniHatasi):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise VeritabaniHatasi(f"Puan düzeltme işlemi başarısız: {str(e)}")