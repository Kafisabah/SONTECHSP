# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.depolar.job_deposu
# Description: E-ticaret iş kuyruğu için repository sınıfı
# Changelog:
# - İlk oluşturma
# - JobDeposu FIFO iş kuyruğu operasyonları eklendi

"""
E-ticaret iş kuyruğu için repository sınıfı.
Asenkron iş kuyruğu yönetimi ve FIFO işleme sağlar.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, asc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ....veritabani.modeller.eticaret import EticaretIsKuyrugu
from ..dto import JobDTO, JobSonucDTO
from ..sabitler import JobDurumlari, YENIDEN_DENEME_ARALIĞI_DAKIKA, MAKSIMUM_YENIDEN_DENEME
from ..hatalar import EntegrasyonHatasi, JobHatasi

logger = logging.getLogger(__name__)


class JobDeposu:
    """
    E-ticaret iş kuyruğu için repository sınıfı.
    
    İş kuyruğu operasyonları:
    - İş ekleme ve durum takibi
    - FIFO sırasında iş çekme
    - Hata yönetimi ve yeniden deneme
    - İş geçmişi ve monitoring
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def job_ekle(self, job_dto: JobDTO) -> int:
        """
        Yeni iş ekler
        
        Args:
            job_dto: İş bilgileri
            
        Returns:
            Oluşturulan işin ID'si
            
        Raises:
            EntegrasyonHatasi: Veritabanı hatası durumunda
        """
        try:
            job = EticaretIsKuyrugu(
                magaza_hesabi_id=job_dto.magaza_hesabi_id,
                tur=job_dto.tur,
                payload_json=job_dto.payload_json,
                durum=job_dto.durum,
                hata_mesaji=job_dto.hata_mesaji,
                deneme_sayisi=job_dto.deneme_sayisi,
                sonraki_deneme=job_dto.sonraki_deneme
            )
            
            self.db.add(job)
            self.db.flush()
            
            logger.info(f"İş eklendi - ID: {job.id}, Tür: {job_dto.tur}, "
                       f"Mağaza: {job_dto.magaza_hesabi_id}")
            
            return job.id
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"İş ekleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "İş eklenemedi - veritabanı hatası",
                detay=str(e)
            )
    
    def job_al(self, limit: int = 10) -> List[EticaretIsKuyrugu]:
        """
        FIFO sırasında bekleyen işleri çeker
        
        Args:
            limit: Maksimum iş sayısı
            
        Returns:
            İş listesi (FIFO sırasında)
        """
        try:
            # Bekleyen veya yeniden deneme zamanı gelen işler
            simdi = datetime.now()
            
            query = self.db.query(EticaretIsKuyrugu).filter(
                or_(
                    EticaretIsKuyrugu.durum == JobDurumlari.BEKLIYOR,
                    and_(
                        EticaretIsKuyrugu.durum == JobDurumlari.HATA,
                        EticaretIsKuyrugu.sonraki_deneme <= simdi,
                        EticaretIsKuyrugu.deneme_sayisi < MAKSIMUM_YENIDEN_DENEME
                    )
                )
            )
            
            # FIFO sırası - en eski işler önce
            joblar = query.order_by(
                asc(EticaretIsKuyrugu.olusturma_zamani)
            ).limit(limit).all()
            
            logger.debug(f"İşler çekildi - Adet: {len(joblar)}")
            
            return joblar
            
        except SQLAlchemyError as e:
            logger.error(f"İş çekme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "İşler çekilemedi - veritabanı hatası",
                detay=str(e)
            )
    
    def job_durum_guncelle(self, job_id: int, sonuc: JobSonucDTO) -> bool:
        """
        İş durumunu günceller
        
        Args:
            job_id: İş ID'si
            sonuc: İş sonucu bilgileri
            
        Returns:
            Güncelleme başarılı ise True
            
        Raises:
            JobHatasi: İş bulunamadığında
            EntegrasyonHatasi: Veritabanı hatası durumunda
        """
        try:
            job = self.db.query(EticaretIsKuyrugu).filter(
                EticaretIsKuyrugu.id == job_id
            ).first()
            
            if not job:
                raise JobHatasi(f"İş bulunamadı", job_id=job_id)
            
            if sonuc.basarili:
                # Başarılı iş
                job.durum = JobDurumlari.GONDERILDI
                job.hata_mesaji = None
                job.sonraki_deneme = None
                
                logger.info(f"İş başarıyla tamamlandı - ID: {job_id}")
                
            else:
                # Başarısız iş - yeniden deneme planla
                job.durum = JobDurumlari.HATA
                job.hata_mesaji = sonuc.hata_mesaji
                job.deneme_sayisi += 1
                
                if job.deneme_sayisi < MAKSIMUM_YENIDEN_DENEME:
                    # Üstel geri çekilme ile yeniden deneme zamanı hesapla
                    dakika_index = min(job.deneme_sayisi - 1, len(YENIDEN_DENEME_ARALIĞI_DAKIKA) - 1)
                    dakika = YENIDEN_DENEME_ARALIĞI_DAKIKA[dakika_index]
                    job.sonraki_deneme = datetime.now() + timedelta(minutes=dakika)
                    
                    logger.warning(f"İş başarısız - yeniden deneme planlandı - ID: {job_id}, "
                                  f"Deneme: {job.deneme_sayisi}, Sonraki: {job.sonraki_deneme}")
                else:
                    # Maksimum deneme aşıldı
                    job.sonraki_deneme = None
                    logger.error(f"İş kalıcı olarak başarısız - ID: {job_id}, "
                                f"Deneme: {job.deneme_sayisi}")
            
            job.guncelleme_zamani = datetime.now()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"İş durum güncelleme hatası - ID: {job_id}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"İş durumu güncellenemedi - ID: {job_id}",
                detay=str(e)
            )
    
    def job_listele(self, magaza_hesabi_id: Optional[int] = None,
                   durum: Optional[str] = None,
                   tur: Optional[str] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[EticaretIsKuyrugu]:
        """
        İşleri listeler (filtreleme ile)
        
        Args:
            magaza_hesabi_id: Mağaza hesabı filtresi
            durum: Durum filtresi
            tur: İş türü filtresi
            limit: Maksimum kayıt sayısı
            offset: Başlangıç offset'i
            
        Returns:
            İş listesi
        """
        try:
            query = self.db.query(EticaretIsKuyrugu)
            
            if magaza_hesabi_id:
                query = query.filter(EticaretIsKuyrugu.magaza_hesabi_id == magaza_hesabi_id)
            if durum:
                query = query.filter(EticaretIsKuyrugu.durum == durum)
            if tur:
                query = query.filter(EticaretIsKuyrugu.tur == tur)
            
            joblar = query.order_by(
                EticaretIsKuyrugu.olusturma_zamani.desc()
            ).limit(limit).offset(offset).all()
            
            logger.debug(f"İşler listelendi - Adet: {len(joblar)}, "
                        f"Mağaza: {magaza_hesabi_id}, Durum: {durum}, Tür: {tur}")
            
            return joblar
            
        except SQLAlchemyError as e:
            logger.error(f"İş listeleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "İşler listelenemedi",
                detay=str(e)
            )
    
    def job_getir(self, job_id: int) -> Optional[EticaretIsKuyrugu]:
        """
        ID'ye göre iş getirir
        
        Args:
            job_id: İş ID'si
            
        Returns:
            İş kaydı veya None
        """
        try:
            job = self.db.query(EticaretIsKuyrugu).filter(
                EticaretIsKuyrugu.id == job_id
            ).first()
            
            return job
            
        except SQLAlchemyError as e:
            logger.error(f"İş getirme hatası - ID: {job_id}, Hata: {str(e)}")
            raise EntegrasyonHatasi(
                f"İş getirilemedi - ID: {job_id}",
                detay=str(e)
            )
    
    def job_istatistikleri(self) -> Dict[str, Any]:
        """
        İş kuyruğu istatistiklerini döndürür
        
        Returns:
            İstatistik bilgileri
        """
        try:
            from sqlalchemy import func
            
            # Durum bazında sayılar
            durum_sayilari = self.db.query(
                EticaretIsKuyrugu.durum,
                func.count(EticaretIsKuyrugu.id).label('sayi')
            ).group_by(EticaretIsKuyrugu.durum).all()
            
            # Tür bazında sayılar
            tur_sayilari = self.db.query(
                EticaretIsKuyrugu.tur,
                func.count(EticaretIsKuyrugu.id).label('sayi')
            ).group_by(EticaretIsKuyrugu.tur).all()
            
            # Bekleyen işler
            bekleyen_sayi = self.db.query(EticaretIsKuyrugu).filter(
                EticaretIsKuyrugu.durum == JobDurumlari.BEKLIYOR
            ).count()
            
            # Yeniden deneme bekleyen işler
            simdi = datetime.now()
            yeniden_deneme_sayi = self.db.query(EticaretIsKuyrugu).filter(
                and_(
                    EticaretIsKuyrugu.durum == JobDurumlari.HATA,
                    EticaretIsKuyrugu.sonraki_deneme <= simdi,
                    EticaretIsKuyrugu.deneme_sayisi < MAKSIMUM_YENIDEN_DENEME
                )
            ).count()
            
            istatistikler = {
                'durum_dagilimi': {durum: sayi for durum, sayi in durum_sayilari},
                'tur_dagilimi': {tur: sayi for tur, sayi in tur_sayilari},
                'bekleyen_is_sayisi': bekleyen_sayi,
                'yeniden_deneme_sayisi': yeniden_deneme_sayi,
                'toplam_is_sayisi': sum(sayi for _, sayi in durum_sayilari)
            }
            
            logger.debug(f"İş kuyruğu istatistikleri: {istatistikler}")
            
            return istatistikler
            
        except SQLAlchemyError as e:
            logger.error(f"İstatistik hesaplama hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "İstatistikler hesaplanamadı",
                detay=str(e)
            )