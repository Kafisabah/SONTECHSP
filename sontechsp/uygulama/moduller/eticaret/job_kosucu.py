# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.job_kosucu
# Description: E-ticaret iş kuyruğu koşucusu
# Changelog:
# - İlk oluşturma
# - JobKoşucusu FIFO iş işleme eklendi

"""
E-ticaret iş kuyruğu koşucusu.
Asenkron işleri FIFO sırasında işler ve hata yönetimi sağlar.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from sqlalchemy.orm import Session

from .depolar import JobDeposu, EticaretDeposu
from .baglanti_fabrikasi import BaglantiFabrikasi
from .dto import JobDTO, JobSonucDTO, StokGuncelleDTO, FiyatGuncelleDTO
from .sabitler import JobTurleri, JobDurumlari
from .hatalar import EntegrasyonHatasi, JobHatasi, PlatformHatasi, VeriDogrulamaHatasi
from .dogrulama import stok_guncellemelerini_dogrula, fiyat_guncellemelerini_dogrula
from ...veritabani.modeller.eticaret import EticaretIsKuyrugu

logger = logging.getLogger(__name__)


class JobKosucu:
    """
    E-ticaret iş kuyruğu koşucusu.
    
    İş işleme operasyonları:
    - FIFO sırasında iş çekme ve işleme
    - Hata yönetimi ve yeniden deneme
    - Batch processing ve performans optimizasyonu
    - İş türüne göre özelleştirilmiş işleme
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.job_deposu = JobDeposu(db_session)
        self.eticaret_deposu = EticaretDeposu(db_session)
        
        # İş türü işleyicileri
        self._job_isleyicileri: Dict[str, Callable] = {
            JobTurleri.SIPARIS_CEK: self._siparis_cek_isle,
            JobTurleri.STOK_GONDER: self._stok_gonder_isle,
            JobTurleri.FIYAT_GONDER: self._fiyat_gonder_isle,
            JobTurleri.DURUM_GUNCELLE: self._durum_guncelle_isle,
        }
    
    def bekleyen_joblari_isle(self, limit: int = 10) -> Dict[str, Any]:
        """
        Bekleyen işleri FIFO sırasında işler
        
        Args:
            limit: Maksimum işlenecek iş sayısı
            
        Returns:
            İşlem sonuç özeti
        """
        logger.info(f"İş kuyruğu işleme başlatılıyor - Limit: {limit}")
        
        sonuc = {
            'islenen_job_sayisi': 0,
            'basarili_job_sayisi': 0,
            'basarisiz_job_sayisi': 0,
            'job_detaylari': []
        }
        
        try:
            # Bekleyen işleri çek
            bekleyen_joblar = self.job_deposu.job_al(limit)
            
            if not bekleyen_joblar:
                logger.debug("İşlenecek iş bulunamadı")
                return sonuc
            
            logger.info(f"İşlenecek iş sayısı: {len(bekleyen_joblar)}")
            
            # Her işi sırayla işle
            for job in bekleyen_joblar:
                job_sonuc = self._job_isle(job)
                
                sonuc['islenen_job_sayisi'] += 1
                if job_sonuc.basarili:
                    sonuc['basarili_job_sayisi'] += 1
                else:
                    sonuc['basarisiz_job_sayisi'] += 1
                
                sonuc['job_detaylari'].append({
                    'job_id': job.id,
                    'tur': job.tur,
                    'basarili': job_sonuc.basarili,
                    'hata_mesaji': job_sonuc.hata_mesaji
                })
            
            logger.info(f"İş kuyruğu işleme tamamlandı - "
                       f"Toplam: {sonuc['islenen_job_sayisi']}, "
                       f"Başarılı: {sonuc['basarili_job_sayisi']}, "
                       f"Başarısız: {sonuc['basarisiz_job_sayisi']}")
            
            return sonuc
            
        except Exception as e:
            logger.error(f"İş kuyruğu işleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "İş kuyruğu işlenemedi",
                detay=str(e)
            )
    
    def job_ekle(self, magaza_hesabi_id: int, job_turu: str, payload: Dict[str, Any]) -> int:
        """
        Yeni iş ekler
        
        Args:
            magaza_hesabi_id: Mağaza hesabı ID'si
            job_turu: İş türü
            payload: İş verisi
            
        Returns:
            Oluşturulan işin ID'si
        """
        try:
            # İş türü validasyonu
            if job_turu not in [t.value for t in JobTurleri]:
                raise JobHatasi(f"Geçersiz iş türü: {job_turu}")
            
            job_dto = JobDTO(
                magaza_hesabi_id=magaza_hesabi_id,
                tur=job_turu,
                payload_json=payload,
                durum=JobDurumlari.BEKLIYOR
            )
            
            job_id = self.job_deposu.job_ekle(job_dto)
            self.db.commit()
            
            logger.info(f"Yeni iş eklendi - ID: {job_id}, Tür: {job_turu}, "
                       f"Mağaza: {magaza_hesabi_id}")
            
            return job_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"İş ekleme hatası: {str(e)}")
            raise EntegrasyonHatasi(
                "İş eklenemedi",
                detay=str(e)
            )
    
    def _job_isle(self, job: EticaretIsKuyrugu) -> JobSonucDTO:
        """
        Tek bir işi işler
        
        Args:
            job: İşlenecek iş
            
        Returns:
            İş sonucu
        """
        logger.debug(f"İş işleniyor - ID: {job.id}, Tür: {job.tur}")
        
        try:
            # İş türüne göre işleyici çağır
            if job.tur not in self._job_isleyicileri:
                raise JobHatasi(f"Desteklenmeyen iş türü: {job.tur}", job_id=job.id)
            
            isleyici = self._job_isleyicileri[job.tur]
            sonuc = isleyici(job)
            
            # İş durumunu güncelle
            self.job_deposu.job_durum_guncelle(job.id, sonuc)
            self.db.commit()
            
            if sonuc.basarili:
                logger.info(f"İş başarıyla işlendi - ID: {job.id}")
            else:
                logger.warning(f"İş başarısız - ID: {job.id}, Hata: {sonuc.hata_mesaji}")
            
            return sonuc
            
        except Exception as e:
            # Beklenmeyen hata
            hata_mesaji = f"İş işleme hatası: {str(e)}"
            logger.error(f"İş işleme hatası - ID: {job.id}, Hata: {hata_mesaji}")
            
            sonuc = JobSonucDTO(
                job_id=job.id,
                basarili=False,
                hata_mesaji=hata_mesaji
            )
            
            try:
                self.job_deposu.job_durum_guncelle(job.id, sonuc)
                self.db.commit()
            except Exception as db_e:
                logger.error(f"İş durum güncelleme hatası - ID: {job.id}, Hata: {str(db_e)}")
                self.db.rollback()
            
            return sonuc
    
    # İş Türü İşleyicileri
    
    def _siparis_cek_isle(self, job: EticaretIsKuyrugu) -> JobSonucDTO:
        """
        Sipariş çekme işini işler
        
        Args:
            job: Sipariş çekme işi
            
        Returns:
            İş sonucu
        """
        try:
            payload = job.payload_json
            sonra = None
            
            # Tarih parametresi varsa parse et
            if 'sonra' in payload and payload['sonra']:
                sonra = datetime.fromisoformat(payload['sonra'])
            
            # Mağaza hesabını getir
            hesap = self.eticaret_deposu.magaza_hesabi_getir(job.magaza_hesabi_id)
            if not hesap or not hesap.aktif_mi:
                raise JobHatasi(f"Mağaza hesabı aktif değil", job_id=job.id)
            
            # Bağlayıcı oluştur
            baglayici = BaglantiFabrikasi.baglayici_olustur(
                hesap.platform,
                hesap.id,
                hesap.kimlik_json,
                hesap.ayar_json
            )
            
            # Siparişleri çek
            siparisler = baglayici.siparisleri_cek(sonra)
            
            # Siparişleri kaydet
            kaydedilen_sayi = 0
            for siparis_dto in siparisler:
                try:
                    self.eticaret_deposu.siparis_kaydet(siparis_dto)
                    kaydedilen_sayi += 1
                except Exception as e:
                    logger.warning(f"Sipariş kaydedilemedi - Sipariş: {siparis_dto.dis_siparis_no}, "
                                  f"Hata: {str(e)}")
            
            return JobSonucDTO(
                job_id=job.id,
                basarili=True,
                sonuc_verisi={
                    'toplam_siparis': len(siparisler),
                    'kaydedilen_siparis': kaydedilen_sayi
                }
            )
            
        except Exception as e:
            return JobSonucDTO(
                job_id=job.id,
                basarili=False,
                hata_mesaji=str(e)
            )
    
    def _stok_gonder_isle(self, job: EticaretIsKuyrugu) -> JobSonucDTO:
        """
        Stok gönderme işini işler
        
        Args:
            job: Stok gönderme işi
            
        Returns:
            İş sonucu
        """
        try:
            payload = job.payload_json
            
            # Stok güncellemelerini parse et
            stok_guncellemeleri = []
            for item in payload.get('stok_guncellemeleri', []):
                stok_dto = StokGuncelleDTO(
                    urun_id=item['urun_id'],
                    depo_id=item['depo_id'],
                    miktar=item['miktar']
                )
                stok_guncellemeleri.append(stok_dto)
            
            if not stok_guncellemeleri:
                raise JobHatasi("Stok güncellemesi bulunamadı", job_id=job.id)
            
            # Stok güncellemelerini doğrula
            try:
                stok_guncellemelerini_dogrula(stok_guncellemeleri)
            except VeriDogrulamaHatasi as e:
                raise JobHatasi(f"Stok doğrulama hatası: {e.mesaj}", job_id=job.id)
            
            # Mağaza hesabını getir
            hesap = self.eticaret_deposu.magaza_hesabi_getir(job.magaza_hesabi_id)
            if not hesap or not hesap.aktif_mi:
                raise JobHatasi(f"Mağaza hesabı aktif değil", job_id=job.id)
            
            # Bağlayıcı oluştur
            baglayici = BaglantiFabrikasi.baglayici_olustur(
                hesap.platform,
                hesap.id,
                hesap.kimlik_json,
                hesap.ayar_json
            )
            
            # Stok güncellemelerini gönder
            baglayici.stok_gonder(stok_guncellemeleri)
            
            return JobSonucDTO(
                job_id=job.id,
                basarili=True,
                sonuc_verisi={
                    'gonderilen_stok_sayisi': len(stok_guncellemeleri)
                }
            )
            
        except Exception as e:
            return JobSonucDTO(
                job_id=job.id,
                basarili=False,
                hata_mesaji=str(e)
            )
    
    def _fiyat_gonder_isle(self, job: EticaretIsKuyrugu) -> JobSonucDTO:
        """
        Fiyat gönderme işini işler
        
        Args:
            job: Fiyat gönderme işi
            
        Returns:
            İş sonucu
        """
        try:
            payload = job.payload_json
            
            # Fiyat güncellemelerini parse et
            fiyat_guncellemeleri = []
            for item in payload.get('fiyat_guncellemeleri', []):
                fiyat_dto = FiyatGuncelleDTO(
                    urun_id=item['urun_id'],
                    fiyat=item['fiyat'],
                    para_birimi=item.get('para_birimi', 'TRY')
                )
                fiyat_guncellemeleri.append(fiyat_dto)
            
            if not fiyat_guncellemeleri:
                raise JobHatasi("Fiyat güncellemesi bulunamadı", job_id=job.id)
            
            # Fiyat güncellemelerini doğrula
            try:
                fiyat_guncellemelerini_dogrula(fiyat_guncellemeleri)
            except VeriDogrulamaHatasi as e:
                raise JobHatasi(f"Fiyat doğrulama hatası: {e.mesaj}", job_id=job.id)
            
            # Mağaza hesabını getir
            hesap = self.eticaret_deposu.magaza_hesabi_getir(job.magaza_hesabi_id)
            if not hesap or not hesap.aktif_mi:
                raise JobHatasi(f"Mağaza hesabı aktif değil", job_id=job.id)
            
            # Bağlayıcı oluştur
            baglayici = BaglantiFabrikasi.baglayici_olustur(
                hesap.platform,
                hesap.id,
                hesap.kimlik_json,
                hesap.ayar_json
            )
            
            # Fiyat güncellemelerini gönder
            baglayici.fiyat_gonder(fiyat_guncellemeleri)
            
            return JobSonucDTO(
                job_id=job.id,
                basarili=True,
                sonuc_verisi={
                    'gonderilen_fiyat_sayisi': len(fiyat_guncellemeleri)
                }
            )
            
        except Exception as e:
            return JobSonucDTO(
                job_id=job.id,
                basarili=False,
                hata_mesaji=str(e)
            )
    
    def _durum_guncelle_isle(self, job: EticaretIsKuyrugu) -> JobSonucDTO:
        """
        Durum güncelleme işini işler
        
        Args:
            job: Durum güncelleme işi
            
        Returns:
            İş sonucu
        """
        try:
            payload = job.payload_json
            
            dis_siparis_no = payload.get('dis_siparis_no')
            yeni_durum = payload.get('yeni_durum')
            takip_no = payload.get('takip_no')
            
            if not dis_siparis_no or not yeni_durum:
                raise JobHatasi("Sipariş numarası veya durum eksik", job_id=job.id)
            
            # Mağaza hesabını getir
            hesap = self.eticaret_deposu.magaza_hesabi_getir(job.magaza_hesabi_id)
            if not hesap or not hesap.aktif_mi:
                raise JobHatasi(f"Mağaza hesabı aktif değil", job_id=job.id)
            
            # Bağlayıcı oluştur
            baglayici = BaglantiFabrikasi.baglayici_olustur(
                hesap.platform,
                hesap.id,
                hesap.kimlik_json,
                hesap.ayar_json
            )
            
            # Durum güncellemesini gönder
            baglayici.siparis_durum_guncelle(dis_siparis_no, yeni_durum, takip_no)
            
            return JobSonucDTO(
                job_id=job.id,
                basarili=True,
                sonuc_verisi={
                    'dis_siparis_no': dis_siparis_no,
                    'yeni_durum': yeni_durum,
                    'takip_no': takip_no
                }
            )
            
        except Exception as e:
            return JobSonucDTO(
                job_id=job.id,
                basarili=False,
                hata_mesaji=str(e)
            )