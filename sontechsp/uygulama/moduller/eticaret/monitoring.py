# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.monitoring
# Description: E-ticaret entegrasyon monitoring ve hata yönetimi
# Changelog:
# - İlk oluşturma
# - HataYoneticisi ve MonitoringServisi eklendi

"""
E-ticaret entegrasyon monitoring ve hata yönetimi.
Detaylı hata loglama, monitoring ve alerting sağlar.
"""

import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy.orm import Session

from .depolar import JobDeposu
from .sabitler import JobDurumlari, JobTurleri
from .hatalar import EntegrasyonHatasi

logger = logging.getLogger(__name__)


class HataSeviyesi(str, Enum):
    """Hata seviyeleri"""
    BILGI = "BILGI"
    UYARI = "UYARI"
    HATA = "HATA"
    KRITIK = "KRITIK"


@dataclass
class HataKaydi:
    """Hata kaydı veri yapısı"""
    zaman: datetime
    seviye: HataSeviyesi
    mesaj: str
    detay: Optional[str] = None
    kaynak: Optional[str] = None
    magaza_hesabi_id: Optional[int] = None
    job_id: Optional[int] = None
    platform: Optional[str] = None
    stack_trace: Optional[str] = None
    ek_bilgiler: Dict[str, Any] = field(default_factory=dict)


class HataYoneticisi:
    """
    Kapsamlı hata yönetimi sınıfı.
    
    Özellikler:
    - Detaylı hata loglama
    - Hata kategorilendirme
    - Stack trace yakalama
    - Bağlam bilgisi toplama
    """
    
    def __init__(self):
        self.hata_kayitlari: List[HataKaydi] = []
        self.hata_sayaclari: Dict[str, int] = {}
        self.son_hatalar: Dict[str, datetime] = {}
    
    def hata_kaydet(self, 
                   seviye: HataSeviyesi,
                   mesaj: str,
                   detay: Optional[str] = None,
                   kaynak: Optional[str] = None,
                   magaza_hesabi_id: Optional[int] = None,
                   job_id: Optional[int] = None,
                   platform: Optional[str] = None,
                   exception: Optional[Exception] = None,
                   ek_bilgiler: Optional[Dict[str, Any]] = None) -> None:
        """
        Hata kaydeder
        
        Args:
            seviye: Hata seviyesi
            mesaj: Hata mesajı
            detay: Detaylı açıklama
            kaynak: Hata kaynağı (fonksiyon/sınıf adı)
            magaza_hesabi_id: İlgili mağaza hesabı
            job_id: İlgili iş ID'si
            platform: İlgili platform
            exception: Exception nesnesi
            ek_bilgiler: Ek bağlam bilgileri
        """
        # Stack trace yakala
        stack_trace = None
        if exception:
            stack_trace = traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
            stack_trace = ''.join(stack_trace)
        
        # Hata kaydı oluştur
        hata_kaydi = HataKaydi(
            zaman=datetime.now(),
            seviye=seviye,
            mesaj=mesaj,
            detay=detay,
            kaynak=kaynak,
            magaza_hesabi_id=magaza_hesabi_id,
            job_id=job_id,
            platform=platform,
            stack_trace=stack_trace,
            ek_bilgiler=ek_bilgiler or {}
        )
        
        # Kayıt listesine ekle
        self.hata_kayitlari.append(hata_kaydi)
        
        # Sayaçları güncelle
        anahtar = f"{seviye.value}_{kaynak or 'unknown'}"
        self.hata_sayaclari[anahtar] = self.hata_sayaclari.get(anahtar, 0) + 1
        self.son_hatalar[anahtar] = datetime.now()
        
        # Log seviyesine göre kaydet
        log_mesaji = f"[{kaynak or 'UNKNOWN'}] {mesaj}"
        if detay:
            log_mesaji += f" - {detay}"
        
        if magaza_hesabi_id:
            log_mesaji += f" (Mağaza: {magaza_hesabi_id})"
        if job_id:
            log_mesaji += f" (Job: {job_id})"
        if platform:
            log_mesaji += f" (Platform: {platform})"
        
        if seviye == HataSeviyesi.BILGI:
            logger.info(log_mesaji)
        elif seviye == HataSeviyesi.UYARI:
            logger.warning(log_mesaji)
        elif seviye == HataSeviyesi.HATA:
            logger.error(log_mesaji)
        elif seviye == HataSeviyesi.KRITIK:
            logger.critical(log_mesaji)
        
        # Stack trace'i ayrı logla
        if stack_trace and seviye in [HataSeviyesi.HATA, HataSeviyesi.KRITIK]:
            logger.error(f"Stack trace for {kaynak}: {stack_trace}")
        
        # Kritik hatalar için immediate alert (gelecekte implement edilebilir)
        if seviye == HataSeviyesi.KRITIK:
            self._kritik_hata_alert(hata_kaydi)
    
    def son_hatalari_getir(self, limit: int = 50) -> List[HataKaydi]:
        """
        Son hataları getirir
        
        Args:
            limit: Maksimum kayıt sayısı
            
        Returns:
            Hata kayıtları listesi
        """
        return sorted(self.hata_kayitlari, key=lambda x: x.zaman, reverse=True)[:limit]
    
    def hata_istatistikleri(self, son_dakika: int = 60) -> Dict[str, Any]:
        """
        Hata istatistiklerini döndürür
        
        Args:
            son_dakika: Son X dakikadaki hatalar
            
        Returns:
            İstatistik bilgileri
        """
        simdi = datetime.now()
        baslangic = simdi - timedelta(minutes=son_dakika)
        
        # Son dakikadaki hatalar
        son_hatalar = [
            h for h in self.hata_kayitlari 
            if h.zaman >= baslangic
        ]
        
        # Seviye bazında sayım
        seviye_sayilari = {}
        for seviye in HataSeviyesi:
            seviye_sayilari[seviye.value] = len([
                h for h in son_hatalar if h.seviye == seviye
            ])
        
        # Platform bazında sayım
        platform_sayilari = {}
        for hata in son_hatalar:
            if hata.platform:
                platform_sayilari[hata.platform] = platform_sayilari.get(hata.platform, 0) + 1
        
        # Kaynak bazında sayım
        kaynak_sayilari = {}
        for hata in son_hatalar:
            if hata.kaynak:
                kaynak_sayilari[hata.kaynak] = kaynak_sayilari.get(hata.kaynak, 0) + 1
        
        return {
            'zaman_araligi_dakika': son_dakika,
            'toplam_hata_sayisi': len(son_hatalar),
            'seviye_dagilimi': seviye_sayilari,
            'platform_dagilimi': platform_sayilari,
            'kaynak_dagilimi': kaynak_sayilari,
            'toplam_kayit_sayisi': len(self.hata_kayitlari)
        }
    
    def _kritik_hata_alert(self, hata_kaydi: HataKaydi) -> None:
        """
        Kritik hata alerti gönderir (placeholder)
        
        Args:
            hata_kaydi: Kritik hata kaydı
        """
        # Gelecekte email, SMS, Slack vb. entegrasyonları eklenebilir
        logger.critical(f"KRITIK HATA ALERT: {hata_kaydi.mesaj}")


class MonitoringServisi:
    """
    E-ticaret entegrasyon monitoring servisi.
    
    Özellikler:
    - İş kuyruğu sağlık kontrolü
    - Performans metrikleri
    - Hata oranı takibi
    - Sistem durumu raporlama
    """
    
    def __init__(self, db_session: Session, hata_yoneticisi: HataYoneticisi):
        self.db = db_session
        self.job_deposu = JobDeposu(db_session)
        self.hata_yoneticisi = hata_yoneticisi
    
    def sistem_durumu(self) -> Dict[str, Any]:
        """
        Genel sistem durumunu döndürür
        
        Returns:
            Sistem durumu bilgileri
        """
        try:
            # İş kuyruğu istatistikleri
            job_istatistikleri = self.job_deposu.job_istatistikleri()
            
            # Hata istatistikleri
            hata_istatistikleri = self.hata_yoneticisi.hata_istatistikleri(60)  # Son 1 saat
            
            # Sağlık skoru hesapla
            saglik_skoru = self._saglik_skoru_hesapla(job_istatistikleri, hata_istatistikleri)
            
            return {
                'zaman': datetime.now().isoformat(),
                'saglik_skoru': saglik_skoru,
                'durum': self._durum_belirle(saglik_skoru),
                'job_kuyrugu': job_istatistikleri,
                'hata_bilgileri': hata_istatistikleri,
                'uyarilar': self._uyari_listesi_olustur(job_istatistikleri, hata_istatistikleri)
            }
            
        except Exception as e:
            self.hata_yoneticisi.hata_kaydet(
                HataSeviyesi.HATA,
                "Sistem durumu alınamadı",
                detay=str(e),
                kaynak="MonitoringServisi.sistem_durumu",
                exception=e
            )
            
            return {
                'zaman': datetime.now().isoformat(),
                'saglik_skoru': 0,
                'durum': 'HATA',
                'hata': str(e)
            }
    
    def job_kuyrugu_sagligi(self) -> Dict[str, Any]:
        """
        İş kuyruğu sağlık durumunu kontrol eder
        
        Returns:
            İş kuyruğu sağlık bilgileri
        """
        try:
            istatistikler = self.job_deposu.job_istatistikleri()
            
            bekleyen_is_sayisi = istatistikler.get('bekleyen_is_sayisi', 0)
            yeniden_deneme_sayisi = istatistikler.get('yeniden_deneme_sayisi', 0)
            toplam_is_sayisi = istatistikler.get('toplam_is_sayisi', 0)
            
            # Sağlık değerlendirmesi
            uyarilar = []
            
            if bekleyen_is_sayisi > 100:
                uyarilar.append(f"Yüksek bekleyen iş sayısı: {bekleyen_is_sayisi}")
            
            if yeniden_deneme_sayisi > 50:
                uyarilar.append(f"Yüksek yeniden deneme sayısı: {yeniden_deneme_sayisi}")
            
            # Hata oranı hesapla
            hata_sayisi = istatistikler.get('durum_dagilimi', {}).get(JobDurumlari.HATA, 0)
            hata_orani = (hata_sayisi / toplam_is_sayisi * 100) if toplam_is_sayisi > 0 else 0
            
            if hata_orani > 10:
                uyarilar.append(f"Yüksek hata oranı: %{hata_orani:.1f}")
            
            durum = "SAGLIKLI" if not uyarilar else "UYARI" if len(uyarilar) <= 2 else "KRITIK"
            
            return {
                'durum': durum,
                'istatistikler': istatistikler,
                'hata_orani_yuzde': round(hata_orani, 1),
                'uyarilar': uyarilar
            }
            
        except Exception as e:
            self.hata_yoneticisi.hata_kaydet(
                HataSeviyesi.HATA,
                "İş kuyruğu sağlık kontrolü başarısız",
                detay=str(e),
                kaynak="MonitoringServisi.job_kuyrugu_sagligi",
                exception=e
            )
            
            return {
                'durum': 'HATA',
                'hata': str(e)
            }
    
    def _saglik_skoru_hesapla(self, job_stats: Dict[str, Any], hata_stats: Dict[str, Any]) -> int:
        """
        Sistem sağlık skoru hesaplar (0-100)
        
        Args:
            job_stats: İş istatistikleri
            hata_stats: Hata istatistikleri
            
        Returns:
            Sağlık skoru (0-100)
        """
        skor = 100
        
        # İş kuyruğu faktörleri
        bekleyen_is = job_stats.get('bekleyen_is_sayisi', 0)
        if bekleyen_is > 50:
            skor -= min(30, bekleyen_is // 10)
        
        yeniden_deneme = job_stats.get('yeniden_deneme_sayisi', 0)
        if yeniden_deneme > 20:
            skor -= min(20, yeniden_deneme // 5)
        
        # Hata faktörleri
        kritik_hatalar = hata_stats.get('seviye_dagilimi', {}).get(HataSeviyesi.KRITIK.value, 0)
        if kritik_hatalar > 0:
            skor -= min(40, kritik_hatalar * 10)
        
        hatalar = hata_stats.get('seviye_dagilimi', {}).get(HataSeviyesi.HATA.value, 0)
        if hatalar > 5:
            skor -= min(20, hatalar * 2)
        
        return max(0, skor)
    
    def _durum_belirle(self, saglik_skoru: int) -> str:
        """
        Sağlık skoruna göre durum belirler
        
        Args:
            saglik_skoru: Sağlık skoru (0-100)
            
        Returns:
            Durum string'i
        """
        if saglik_skoru >= 80:
            return "SAGLIKLI"
        elif saglik_skoru >= 60:
            return "UYARI"
        elif saglik_skoru >= 30:
            return "KRITIK"
        else:
            return "HATA"
    
    def _uyari_listesi_olustur(self, job_stats: Dict[str, Any], hata_stats: Dict[str, Any]) -> List[str]:
        """
        Uyarı listesi oluşturur
        
        Args:
            job_stats: İş istatistikleri
            hata_stats: Hata istatistikleri
            
        Returns:
            Uyarı mesajları listesi
        """
        uyarilar = []
        
        # İş kuyruğu uyarıları
        bekleyen_is = job_stats.get('bekleyen_is_sayisi', 0)
        if bekleyen_is > 100:
            uyarilar.append(f"Yüksek bekleyen iş sayısı: {bekleyen_is}")
        
        # Hata uyarıları
        kritik_hatalar = hata_stats.get('seviye_dagilimi', {}).get(HataSeviyesi.KRITIK.value, 0)
        if kritik_hatalar > 0:
            uyarilar.append(f"Kritik hata tespit edildi: {kritik_hatalar} adet")
        
        return uyarilar


# Global monitoring instance'ları
_hata_yoneticisi: Optional[HataYoneticisi] = None
_monitoring_servisi: Optional[MonitoringServisi] = None


def hata_yoneticisi_al() -> HataYoneticisi:
    """
    Global hata yöneticisi instance'ını döndürür (singleton pattern)
    
    Returns:
        HataYoneticisi instance'ı
    """
    global _hata_yoneticisi
    
    if _hata_yoneticisi is None:
        _hata_yoneticisi = HataYoneticisi()
    
    return _hata_yoneticisi


def monitoring_servisi_al(db_session: Session) -> MonitoringServisi:
    """
    Monitoring servisi instance'ını döndürür
    
    Args:
        db_session: Veritabanı session'ı
        
    Returns:
        MonitoringServisi instance'ı
    """
    global _monitoring_servisi
    
    if _monitoring_servisi is None:
        _monitoring_servisi = MonitoringServisi(db_session, hata_yoneticisi_al())
    
    return _monitoring_servisi


# Kolaylık fonksiyonları

def hata_kaydet(seviye: HataSeviyesi, mesaj: str, **kwargs) -> None:
    """
    Hata kaydeder (kolaylık fonksiyonu)
    
    Args:
        seviye: Hata seviyesi
        mesaj: Hata mesajı
        **kwargs: Ek parametreler
    """
    hata_yoneticisi = hata_yoneticisi_al()
    hata_yoneticisi.hata_kaydet(seviye, mesaj, **kwargs)